export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://localhost:8000";

export type Platform = "x" | "reddit";

export interface Account {
  id: number;
  platform: string;
  label: string;
  status: string;
  last_error: string | null;
  last_synced_at: string | null;
  created_at: string;
  extra_json: Record<string, unknown>;
}

export interface Bookmark {
  id: number;
  account_id: number;
  platform: string;
  external_id: string;
  url: string;
  title: string | null;
  text: string | null;
  author_handle: string | null;
  author_name: string | null;
  media_json: Array<{ type: string; url: string; poster?: string }>;
  saved_at: string | null;
  fetched_at: string;
  archived: boolean;
}

export interface BookmarkList {
  items: Bookmark[];
  total: number;
  limit: number;
  offset: number;
}

export interface SyncRun {
  id: number;
  account_id: number;
  started_at: string;
  finished_at: string | null;
  ok: boolean;
  new_count: number;
  error: string | null;
}

export type VaultDirSource = "env" | "user_config" | "default";

export interface VaultSettings {
  path: string;
  source: VaultDirSource;
  env_override_active: boolean;
  exists: boolean;
  file_count: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listAccounts: () => request<Account[]>("/accounts"),
  createAccount: (payload: {
    platform: Platform;
    label: string;
    raw_cookies: string;
    username?: string;
  }) =>
    request<Account>("/accounts", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateCookies: (
    id: number,
    payload: {
      platform: Platform;
      label: string;
      raw_cookies: string;
      username?: string;
    },
  ) =>
    request<Account>(`/accounts/${id}/cookies`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteAccount: (id: number) =>
    request<void>(`/accounts/${id}`, { method: "DELETE" }),
  syncNow: (id: number) =>
    request<SyncRun>(`/accounts/${id}/sync`, { method: "POST" }),

  listBookmarks: (params: {
    platform?: string;
    archived?: boolean;
    q?: string;
    limit?: number;
    offset?: number;
  }) => {
    const qs = new URLSearchParams();
    if (params.platform) qs.set("platform", params.platform);
    qs.set("archived", String(params.archived ?? false));
    if (params.q) qs.set("q", params.q);
    qs.set("limit", String(params.limit ?? 50));
    qs.set("offset", String(params.offset ?? 0));
    return request<BookmarkList>(`/bookmarks?${qs.toString()}`);
  },
  setArchived: (id: number, archived: boolean) =>
    request<Bookmark>(`/bookmarks/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ archived }),
    }),

  getVaultSettings: () => request<VaultSettings>("/settings/vault"),
  updateVaultSettings: (payload: { path: string; move: boolean }) =>
    request<VaultSettings>("/settings/vault", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};
