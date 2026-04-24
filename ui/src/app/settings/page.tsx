"use client";

import { useCallback, useEffect, useState } from "react";
import {
  api,
  type Account,
  type Platform,
  type SyncRun,
  type VaultSettings,
} from "@/lib/api";
import {
  Badge,
  Button,
  Card,
  Input,
  Select,
  Textarea,
  platformBadge,
  statusBadge,
} from "@/components/ui";

export default function SettingsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setAccounts(await api.listAccounts());
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function syncNow(id: number) {
    setBusyId(id);
    setError(null);
    setMessage(null);
    try {
      const run: SyncRun = await api.syncNow(id);
      setMessage(
        run.ok
          ? `Synced: ${run.new_count} new item${run.new_count === 1 ? "" : "s"}.`
          : `Sync failed: ${run.error ?? "unknown error"}`,
      );
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  async function remove(id: number) {
    if (!confirm("Delete this account and all its bookmarks?")) return;
    setBusyId(id);
    try {
      await api.deleteAccount(id);
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-6">
      <VaultSection />

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Accounts</h2>
        {accounts.length === 0 && (
          <Card className="text-sm text-zinc-500">
            No accounts yet. Add one below.
          </Card>
        )}
        {message && (
          <Card className="text-sm text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900">
            {message}
          </Card>
        )}
        {error && (
          <Card className="text-sm text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-900">
            {error}
          </Card>
        )}
        <div className="space-y-2">
          {accounts.map((a) => (
            <Card key={a.id} className="flex items-center justify-between gap-3">
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  {platformBadge(a.platform)}
                  <span className="font-medium">{a.label}</span>
                  {statusBadge(a.status)}
                </div>
                <div className="text-xs text-zinc-500">
                  {a.last_synced_at
                    ? `Last synced ${new Date(a.last_synced_at).toLocaleString()}`
                    : "Never synced"}
                  {a.last_error ? ` — ${a.last_error}` : ""}
                  {a.platform === "reddit" && a.extra_json?.username
                    ? ` — u/${String(a.extra_json.username)}`
                    : ""}
                </div>
              </div>
              <div className="flex gap-2 shrink-0">
                <Button
                  variant="ghost"
                  onClick={() => syncNow(a.id)}
                  disabled={busyId === a.id}
                >
                  {busyId === a.id ? "Working..." : "Sync now"}
                </Button>
                <Button
                  variant="danger"
                  onClick={() => remove(a.id)}
                  disabled={busyId === a.id}
                >
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Add or update account</h2>
        <AccountForm
          accounts={accounts}
          onDone={() => {
            setMessage("Account saved. Initial sync started in background.");
            load();
          }}
          onError={(e) => setError(e)}
        />
        <Card className="mt-3 text-xs text-zinc-500 leading-relaxed">
          <div className="font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
            How to get your cookies
          </div>
          <ol className="list-decimal pl-5 space-y-1">
            <li>
              Open <strong>x.com/i/bookmarks</strong> or <strong>reddit.com</strong>{" "}
              while logged in.
            </li>
            <li>
              Open DevTools (F12) → <strong>Network</strong> tab. Filter{" "}
              <code>Doc</code> or <code>Fetch/XHR</code>.
            </li>
            <li>Click any request, find the <strong>Cookie</strong> request header.</li>
            <li>
              Right-click → <strong>Copy value</strong>, then paste it below. We only
              keep the fields we need.
            </li>
          </ol>
        </Card>
      </section>
    </div>
  );
}

function AccountForm({
  accounts,
  onDone,
  onError,
}: {
  accounts: Account[];
  onDone: () => void;
  onError: (msg: string) => void;
}) {
  const [platform, setPlatform] = useState<Platform>("x");
  const [label, setLabel] = useState("");
  const [username, setUsername] = useState("");
  const [rawCookies, setRawCookies] = useState("");
  const [existingId, setExistingId] = useState<number | "">("");
  const [submitting, setSubmitting] = useState(false);

  const platformAccounts = accounts.filter((a) => a.platform === platform);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (existingId !== "") {
        await api.updateCookies(existingId, {
          platform,
          label: label || accounts.find((a) => a.id === existingId)?.label || "main",
          raw_cookies: rawCookies,
          username: username || undefined,
        });
      } else {
        await api.createAccount({
          platform,
          label: label || "main",
          raw_cookies: rawCookies,
          username: username || undefined,
        });
      }
      setRawCookies("");
      setLabel("");
      setUsername("");
      setExistingId("");
      onDone();
    } catch (err) {
      onError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <form onSubmit={onSubmit} className="grid gap-3">
        <div className="grid gap-3 sm:grid-cols-3">
          <label className="text-sm">
            <div className="text-xs text-zinc-500 mb-1">Platform</div>
            <Select
              value={platform}
              onChange={(e) => {
                setPlatform(e.target.value as Platform);
                setExistingId("");
              }}
              className="w-full"
            >
              <option value="x">X (Twitter)</option>
              <option value="reddit">Reddit</option>
            </Select>
          </label>
          <label className="text-sm">
            <div className="text-xs text-zinc-500 mb-1">Update existing</div>
            <Select
              value={existingId}
              onChange={(e) =>
                setExistingId(e.target.value === "" ? "" : Number(e.target.value))
              }
              className="w-full"
            >
              <option value="">— new account —</option>
              {platformAccounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.label}
                </option>
              ))}
            </Select>
          </label>
          <label className="text-sm">
            <div className="text-xs text-zinc-500 mb-1">Label</div>
            <Input
              placeholder="main"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
            />
          </label>
        </div>

        {platform === "reddit" && (
          <label className="text-sm">
            <div className="text-xs text-zinc-500 mb-1">
              Reddit username (without u/)
            </div>
            <Input
              placeholder="your_username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </label>
        )}

        <label className="text-sm">
          <div className="text-xs text-zinc-500 mb-1">
            Paste the full <code>Cookie</code> header
          </div>
          <Textarea
            rows={5}
            placeholder={
              platform === "x"
                ? "auth_token=...; ct0=...; (paste the full Cookie: header)"
                : "reddit_session=...; token_v2=...; (paste the full Cookie: header)"
            }
            value={rawCookies}
            onChange={(e) => setRawCookies(e.target.value)}
            required
          />
        </label>

        <div className="flex justify-end">
          <Button type="submit" disabled={submitting}>
            {submitting
              ? "Saving..."
              : existingId !== ""
                ? "Update cookies"
                : "Add account"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

function sourceBadge(source: VaultSettings["source"]) {
  if (source === "env") return <Badge color="orange">env override</Badge>;
  if (source === "user_config") return <Badge color="blue">user</Badge>;
  return <Badge color="zinc">default</Badge>;
}

function VaultSection() {
  const [current, setCurrent] = useState<VaultSettings | null>(null);
  const [pending, setPending] = useState("");
  const [busy, setBusy] = useState<false | "save" | "move">(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const s = await api.getVaultSettings();
      setCurrent(s);
      setPending((prev) => (prev === "" ? s.path : prev));
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function submit(move: boolean) {
    if (!current) return;
    const trimmed = pending.trim();
    if (!trimmed) {
      setError("Path cannot be empty.");
      return;
    }
    if (move && trimmed === current.path) {
      setError("New path is the same as the current one — nothing to move.");
      return;
    }
    if (
      move &&
      !confirm(
        `Move ${current.file_count} vault file${current.file_count === 1 ? "" : "s"} from\n  ${current.path}\nto\n  ${trimmed}?\n\nDestination must be empty or nonexistent.`,
      )
    ) {
      return;
    }
    setBusy(move ? "move" : "save");
    setError(null);
    setMessage(null);
    try {
      const next = await api.updateVaultSettings({ path: trimmed, move });
      setCurrent(next);
      setPending(next.path);
      setMessage(
        move
          ? `Moved vault to ${next.path}. ${next.file_count} file${next.file_count === 1 ? "" : "s"} now live there.`
          : `Saved. Future syncs will write to ${next.path}.`,
      );
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold">Vault</h2>
      <Card className="space-y-3">
        {current === null ? (
          <div className="text-sm text-zinc-500">Loading…</div>
        ) : (
          <>
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-zinc-500">Current:</span>
                <code className="font-mono text-xs break-all text-zinc-800 dark:text-zinc-200">
                  {current.path}
                </code>
                {sourceBadge(current.source)}
                {current.exists ? (
                  <Badge color="green">
                    {current.file_count} file{current.file_count === 1 ? "" : "s"}
                  </Badge>
                ) : (
                  <Badge color="red">missing</Badge>
                )}
              </div>
              {current.env_override_active && (
                <div className="text-xs text-orange-700 dark:text-orange-300">
                  <code>VAULT_DIR</code> is set in the environment, so it overrides
                  whatever you save here. Unset it (remove from <code>.env</code>
                  {" "}and restart) to let the UI preference take effect.
                </div>
              )}
            </div>

            <label className="text-sm block">
              <div className="text-xs text-zinc-500 mb-1">
                New path (absolute, or starting with <code>~</code>)
              </div>
              <Input
                value={pending}
                onChange={(e) => setPending(e.target.value)}
                placeholder="/home/you/Documents/bookmark-vault"
                className="font-mono text-xs"
              />
            </label>

            {message && (
              <div className="text-sm text-emerald-700 dark:text-emerald-300">
                {message}
              </div>
            )}
            {error && (
              <div className="text-sm text-rose-700 dark:text-rose-300">{error}</div>
            )}

            <div className="flex flex-wrap justify-end gap-2">
              <Button
                variant="ghost"
                onClick={() => submit(false)}
                disabled={busy !== false || pending.trim() === current.path}
                title="Persist the new path. Existing files are left where they are; future syncs write to the new path."
              >
                {busy === "save" ? "Saving…" : "Save path"}
              </Button>
              <Button
                onClick={() => submit(true)}
                disabled={
                  busy !== false ||
                  current.env_override_active ||
                  pending.trim() === current.path
                }
                title={
                  current.env_override_active
                    ? "Disabled because VAULT_DIR env is set."
                    : "Move the current vault contents to the new path, then persist."
                }
              >
                {busy === "move" ? "Moving…" : "Save + move contents"}
              </Button>
            </div>

            <div className="text-xs text-zinc-500 leading-relaxed">
              The vault is the single source of truth: every synced bookmark is
              written as <code>{"<platform>/<external_id>.md"}</code>, and the DB
              can be rebuilt from it with{" "}
              <code>scripts/restore_from_vault.py</code>. Safe to keep on
              Syncthing, iCloud Drive, or an Obsidian workspace.
            </div>
          </>
        )}
      </Card>
    </section>
  );
}
