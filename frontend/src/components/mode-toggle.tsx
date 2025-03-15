"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { IconSun, IconMoon, IconDeviceDesktop } from "@tabler/icons-react";

export function ModeToggle() {
  const { setTheme, theme } = useTheme();

  return (
    <div className="flex items-center space-x-2">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setTheme("light")}
        className={theme === "light" ? "text-primary" : "text-muted-foreground"}
      >
        <IconSun className="h-5 w-5" />
        <span className="sr-only">Light mode</span>
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setTheme("dark")}
        className={theme === "dark" ? "text-primary" : "text-muted-foreground"}
      >
        <IconMoon className="h-5 w-5" />
        <span className="sr-only">Dark mode</span>
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setTheme("system")}
        className={
          theme === "system" ? "text-primary" : "text-muted-foreground"
        }
      >
        <IconDeviceDesktop className="h-5 w-5" />
        <span className="sr-only">System mode</span>
      </Button>
    </div>
  );
}
