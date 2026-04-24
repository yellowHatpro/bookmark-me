"""User-editable runtime configuration.

Distinct from `app.config.Settings`:
    * `Settings`  = env-backed, immutable for the life of the process (12-factor).
    * `user_config` = user-editable at runtime via the Settings UI, persisted
      to `~/.config/bookmark-me/config.json` so it survives restarts *and* DB
      wipes (critical: the restore script needs to know where the vault lives
      even when Postgres is empty).

Only one knob lives here today (`vault_dir`), but the JSON-on-disk shape is
forward-compatible -- add new keys without a migration.

Vault directory resolution order (first non-empty wins):
    1. `VAULT_DIR` env var   — explicit override, for Docker/CI.
    2. config.json -> vault_dir   — set via the Settings UI.
    3. Default: `$XDG_CONFIG_HOME/bookmark-me/vault_dir/`
       (falls back to `~/.config/bookmark-me/vault_dir/`).
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

log = logging.getLogger(__name__)

VaultDirSource = Literal["env", "user_config", "default"]


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------


def _xdg_config_home() -> Path:
    """`$XDG_CONFIG_HOME` if set, else `~/.config`."""
    env = os.environ.get("XDG_CONFIG_HOME", "").strip()
    return Path(env).expanduser() if env else Path.home() / ".config"


def user_config_dir() -> Path:
    """Directory for bookmark-me's user-pref file. Created on demand."""
    return _xdg_config_home() / "bookmark-me"


def user_config_path() -> Path:
    return user_config_dir() / "config.json"


def default_vault_dir() -> Path:
    """Default vault location when nothing overrides it."""
    return (user_config_dir() / "vault_dir").resolve()


def _normalize(path: str | os.PathLike[str]) -> Path:
    """Expand `~`, make absolute, but don't require it to exist yet."""
    return Path(os.fspath(path)).expanduser().absolute()


# --------------------------------------------------------------------------
# config.json read/write
# --------------------------------------------------------------------------


def read_config() -> dict[str, Any]:
    """Parse `~/.config/bookmark-me/config.json`. Returns {} on any failure."""
    path = user_config_path()
    if not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("Ignoring unreadable user config at %s: %s", path, exc)
        return {}
    return data if isinstance(data, dict) else {}


def write_config(data: dict[str, Any]) -> None:
    """Atomically persist `data` to `~/.config/bookmark-me/config.json`."""
    path = user_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(prefix=".config.", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        # tmp file still dangles if replace fails; best-effort cleanup.
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------
# Vault dir resolution
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class VaultDirInfo:
    path: Path
    source: VaultDirSource
    env_override_active: bool


def effective_vault_dir_info() -> VaultDirInfo:
    env_val = os.environ.get("VAULT_DIR", "").strip()
    if env_val:
        return VaultDirInfo(_normalize(env_val), "env", True)

    configured = read_config().get("vault_dir")
    if isinstance(configured, str) and configured.strip():
        return VaultDirInfo(_normalize(configured), "user_config", False)

    return VaultDirInfo(default_vault_dir(), "default", False)


def effective_vault_dir() -> Path:
    return effective_vault_dir_info().path


# --------------------------------------------------------------------------
# Updates (called by the /settings/vault PUT handler)
# --------------------------------------------------------------------------


class VaultUpdateError(ValueError):
    """Raised when the new vault path is invalid or the move would be unsafe."""


def set_vault_dir(new_path: str, *, move: bool) -> VaultDirInfo:
    """Persist `new_path` to config.json, optionally moving existing contents.

    Raises VaultUpdateError with a user-facing message on any unsafe condition.
    Does not touch the config file or the filesystem until all preconditions pass.
    """
    if not new_path or not new_path.strip():
        raise VaultUpdateError("Path cannot be empty.")

    dst = _normalize(new_path)
    src = effective_vault_dir()

    # Guard against nested/overlapping paths, which would make the move either
    # a no-op (src == dst) or recursively self-eating. `is_relative_to` on its
    # own returns True for the equal case too, so we compare != src explicitly.
    if dst != src:
        if dst.is_relative_to(src):
            raise VaultUpdateError(
                f"New path '{dst}' is inside the current vault '{src}'. "
                "Pick a path outside the current vault."
            )
        if src.is_relative_to(dst):
            raise VaultUpdateError(
                f"Current vault '{src}' is inside the new path '{dst}'. "
                "Pick a path that doesn't contain the current vault."
            )

    # Reject destinations that exist as a plain file (not a dir).
    if dst.exists() and not dst.is_dir():
        raise VaultUpdateError(f"'{dst}' exists and is not a directory.")

    if move and dst != src:
        if not src.exists():
            raise VaultUpdateError(
                f"Current vault '{src}' doesn't exist yet; nothing to move."
            )
        if dst.exists() and any(dst.iterdir()):
            raise VaultUpdateError(
                f"Destination '{dst}' is not empty. Empty it or pick another path."
            )
        _move_tree(src, dst)

    dst.mkdir(parents=True, exist_ok=True)

    cfg = read_config()
    cfg["vault_dir"] = str(dst)
    write_config(cfg)

    log.info("Vault dir updated: %s -> %s (move=%s)", src, dst, move)
    return effective_vault_dir_info()


def _move_tree(src: Path, dst: Path) -> None:
    """Rename if same filesystem; otherwise copytree + rmtree.

    Uses copytree as the cross-filesystem fallback since shutil.move's semantics
    for existing directory destinations differ between "dst exists" and "dst
    doesn't" in ways that are surprising (it would move src *into* dst).
    """
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.rename(src, dst)
            return
        except OSError:
            # Fall through to copy-then-delete (cross-device, Windows rename-
            # across-drives, etc.).
            pass

    shutil.copytree(src, dst, dirs_exist_ok=True)
    shutil.rmtree(src)
