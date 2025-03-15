import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-background px-2">
      <div className="container flex flex-col items-center justify-between gap-4 py-10 md:h-24 md:flex-row md:py-0">
        <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Built with ❤️ by{" "}
            <Link
              href="https://github.com/yellowhatpro"
              className="font-medium underline underline-offset-4"
            >
              yellowhatpro
            </Link>
            . The source code is available on{" "}
            <Link
              href="https://github.com/yellowhatpro/bookmark-me"
              target="_blank"
              rel="noreferrer"
              className="font-medium underline underline-offset-4"
            >
              GitHub
            </Link>
            .
          </p>
        </div>
      </div>
    </footer>
  );
}
