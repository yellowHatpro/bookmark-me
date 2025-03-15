"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { IconBookmark } from "@tabler/icons-react";
import { ModeToggle } from "@/components/mode-toggle";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function Header() {
  const pathname = usePathname();

  const routes = [
    {
      href: "/",
      label: "Home",
      active: pathname === "/",
    },
    {
      href: "/dashboard",
      label: "Dashboard",
      active: pathname === "/dashboard",
    },
    {
      href: "/bookmarks",
      label: "Bookmarks",
      active: pathname === "/bookmarks",
    },
    {
      href: "/chat",
      label: "Chat",
      active: pathname === "/chat",
    },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="flex items-center space-x-2">
            <IconBookmark className="h-6 w-6" />
            <span className="font-bold">Bookmark Me</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-4">
          <nav className="flex items-center space-x-2">
            {routes.map((route) => (
              <Button
                key={route.href}
                variant="ghost"
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  route.active ? "text-foreground" : "text-foreground/60"
                )}
                asChild
              >
                <Link href={route.href}>{route.label}</Link>
              </Button>
            ))}
          </nav>
          <ModeToggle />
        </div>
      </div>
    </header>
  );
}
