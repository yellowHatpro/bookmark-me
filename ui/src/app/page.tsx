"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { api, type Bookmark, type BookmarkList } from "@/lib/api";
import {
  Badge,
  Button,
  Card,
  Input,
  Select,
  platformBadge,
} from "@/components/ui";

const PAGE_SIZE = 50;

export default function FeedPage() {
  const [platform, setPlatform] = useState<string>("");
  const [archived, setArchived] = useState(false);
  const [q, setQ] = useState("");
  const [queryInput, setQueryInput] = useState("");
  const [data, setData] = useState<BookmarkList | null>(null);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listBookmarks({
        platform: platform || undefined,
        archived,
        q: q || undefined,
        limit: PAGE_SIZE,
        offset,
      });
      setData(res);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [platform, archived, q, offset]);

  useEffect(() => {
    load();
  }, [load]);

  const totalPages = useMemo(() => {
    if (!data) return 0;
    return Math.max(1, Math.ceil(data.total / PAGE_SIZE));
  }, [data]);
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setOffset(0);
    setQ(queryInput.trim());
  };

  async function toggleArchive(b: Bookmark) {
    try {
      await api.setArchived(b.id, !b.archived);
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <form onSubmit={onSearch} className="flex gap-2 flex-1 min-w-[240px]">
          <Input
            placeholder="Search title, text, author..."
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
          />
          <Button type="submit" variant="ghost">
            Search
          </Button>
        </form>

        <Select
          value={platform}
          onChange={(e) => {
            setOffset(0);
            setPlatform(e.target.value);
          }}
        >
          <option value="">All platforms</option>
          <option value="x">X</option>
          <option value="reddit">Reddit</option>
        </Select>

        <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
          <input
            type="checkbox"
            checked={archived}
            onChange={(e) => {
              setOffset(0);
              setArchived(e.target.checked);
            }}
          />
          Archived
        </label>
      </div>

      {error && (
        <Card className="border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-sm">
          {error}
        </Card>
      )}

      {loading && !data && (
        <div className="text-sm text-zinc-500">Loading...</div>
      )}

      {data && data.items.length === 0 && (
        <Card className="text-center text-zinc-500">
          No bookmarks yet. Add an account in{" "}
          <Link href="/settings" className="underline">
            Settings
          </Link>
          .
        </Card>
      )}

      <div className="space-y-3">
        {data?.items.map((b) => (
          <BookmarkCard key={b.id} bookmark={b} onToggleArchive={toggleArchive} />
        ))}
      </div>

      {data && data.total > PAGE_SIZE && (
        <div className="flex items-center justify-between pt-2">
          <div className="text-sm text-zinc-500">
            Page {currentPage} of {totalPages} &middot; {data.total} total
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              disabled={offset === 0 || loading}
              onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            >
              Prev
            </Button>
            <Button
              variant="ghost"
              disabled={offset + PAGE_SIZE >= data.total || loading}
              onClick={() => setOffset(offset + PAGE_SIZE)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function BookmarkCard({
  bookmark,
  onToggleArchive,
}: {
  bookmark: Bookmark;
  onToggleArchive: (b: Bookmark) => void;
}) {
  const savedAt = bookmark.saved_at
    ? new Date(bookmark.saved_at).toLocaleString()
    : null;
  const preview = bookmark.text?.slice(0, 420);

  return (
    <Card>
      <div className="flex items-start gap-3 justify-between">
        <div className="flex items-center gap-2 flex-wrap">
          {platformBadge(bookmark.platform)}
          {bookmark.author_handle && (
            <Badge color="zinc">@{bookmark.author_handle}</Badge>
          )}
          {savedAt && (
            <span className="text-xs text-zinc-500">{savedAt}</span>
          )}
        </div>
        <div className="flex gap-2 shrink-0">
          <a
            href={bookmark.url}
            target="_blank"
            rel="noreferrer"
            className="text-sm underline text-zinc-600 dark:text-zinc-400"
          >
            open
          </a>
          <button
            onClick={() => onToggleArchive(bookmark)}
            className="text-sm text-zinc-600 dark:text-zinc-400 hover:underline"
          >
            {bookmark.archived ? "unarchive" : "archive"}
          </button>
        </div>
      </div>

      {bookmark.title && (
        <h3 className="mt-2 font-medium leading-snug">{bookmark.title}</h3>
      )}
      {preview && (
        <p className="mt-1 whitespace-pre-wrap text-sm text-zinc-700 dark:text-zinc-300 line-clamp-6">
          {preview}
          {bookmark.text && bookmark.text.length > 420 ? "..." : ""}
        </p>
      )}

      {bookmark.media_json.length > 0 && (
        <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 gap-2">
          {bookmark.media_json.slice(0, 6).map((m, i) =>
            m.type === "image" ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                key={i}
                src={m.url}
                alt=""
                className="rounded-md border border-zinc-200 dark:border-zinc-800 w-full h-40 object-cover"
              />
            ) : m.type === "video" ? (
              <video
                key={i}
                src={m.url}
                poster={m.poster}
                controls
                className="rounded-md border border-zinc-200 dark:border-zinc-800 w-full h-40 object-cover"
              />
            ) : null,
          )}
        </div>
      )}
    </Card>
  );
}
