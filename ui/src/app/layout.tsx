import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "bookmark-me",
  description: "Personal aggregator for saved posts across platforms",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
        <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-900/60 backdrop-blur sticky top-0 z-10">
          <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
            <Link href="/" className="font-semibold tracking-tight">
              bookmark-me
            </Link>
            <nav className="flex gap-4 text-sm text-zinc-600 dark:text-zinc-400">
              <Link href="/" className="hover:text-zinc-900 dark:hover:text-zinc-100">
                Feed
              </Link>
              <Link
                href="/settings"
                className="hover:text-zinc-900 dark:hover:text-zinc-100"
              >
                Settings
              </Link>
            </nav>
          </div>
        </header>
        <main className="flex-1 w-full max-w-5xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
