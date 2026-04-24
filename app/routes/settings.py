"""User-facing runtime settings.

Only the vault directory today -- the shape is set up so future user-editable
settings can slot in without rewriting the contract.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app import user_config
from app.schemas import VaultSettings, VaultSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _serialize() -> VaultSettings:
    info = user_config.effective_vault_dir_info()
    path = info.path
    file_count = 0
    if path.exists() and path.is_dir():
        file_count = sum(1 for _ in path.rglob("*.md"))
    return VaultSettings(
        path=str(path),
        source=info.source,
        env_override_active=info.env_override_active,
        exists=path.exists() and path.is_dir(),
        file_count=file_count,
    )


@router.get("/vault", response_model=VaultSettings)
def get_vault_settings() -> VaultSettings:
    return _serialize()


@router.put("/vault", response_model=VaultSettings)
def update_vault_settings(payload: VaultSettingsUpdate) -> VaultSettings:
    if user_config.effective_vault_dir_info().env_override_active:
        # Persisting to config.json is still allowed (so removing the env var
        # later makes the UI preference effective), but silently applying while
        # env pins the real path would be confusing. Reject the move; accept
        # the path update.
        if payload.move:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "VAULT_DIR env var is set; it overrides user settings. "
                    "Unset VAULT_DIR (remove it from .env / compose) before "
                    "moving the vault via the UI."
                ),
            )

    try:
        user_config.set_vault_dir(payload.path, move=payload.move)
    except user_config.VaultUpdateError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return _serialize()
