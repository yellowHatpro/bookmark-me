"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
  IconBrandTwitter,
  IconBrandGoogle,
  IconBrandLinkedin,
  IconSearch,
  IconFilter,
  IconBookmark,
  IconTrash,
  IconEdit,
} from "@tabler/icons-react";
import { Button } from "@/components/ui/button";

const bookmarks = [
  {
    id: 1,
    title: "How to build a modern web application",
    url: "https://twitter.com/user/status/123456789",
    source: "twitter",
    icon: <IconBrandTwitter className="h-5 w-5" />,
    date: "2 hours ago",
  },
  {
    id: 2,
    title: "10 Tips for Better Productivity",
    url: "https://keep.google.com/note/123456789",
    source: "google",
    icon: <IconBrandGoogle className="h-5 w-5" />,
    date: "Yesterday",
  },
  {
    id: 3,
    title: "The Future of AI in Web Development",
    url: "https://linkedin.com/post/123456789",
    source: "linkedin",
    icon: <IconBrandLinkedin className="h-5 w-5" />,
    date: "3 days ago",
  },
  {
    id: 4,
    title: "Understanding React Server Components",
    url: "https://twitter.com/user/status/987654321",
    source: "twitter",
    icon: <IconBrandTwitter className="h-5 w-5" />,
    date: "1 week ago",
  },
  {
    id: 5,
    title: "The Complete Guide to CSS Grid",
    url: "https://keep.google.com/note/987654321",
    source: "google",
    icon: <IconBrandGoogle className="h-5 w-5" />,
    date: "2 weeks ago",
  },
];

export default function BookmarksPage() {
  return (
    <MainLayout>
      <div className="container py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="mb-2 text-3xl font-bold">Bookmarks</h1>
          <p className="text-muted-foreground">
            Manage and organize your saved content from across the web
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="relative">
            <IconSearch className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search bookmarks..."
              className="h-10 w-full rounded-md border border-input bg-background pl-10 pr-4 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 sm:w-[300px]"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <IconFilter className="mr-2 h-4 w-4" />
              Filter
            </Button>
            <Button size="sm">
              <IconBookmark className="mr-2 h-4 w-4" />
              Add Bookmark
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Tabs defaultValue="all">
            <TabsList>
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="twitter">Twitter</TabsTrigger>
              <TabsTrigger value="google">Google Keep</TabsTrigger>
              <TabsTrigger value="linkedin">LinkedIn</TabsTrigger>
            </TabsList>
            <TabsContent value="all" className="mt-6">
              <div className="grid gap-4">
                {bookmarks.map((bookmark, index) => (
                  <motion.div
                    key={bookmark.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                  >
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-4">
                          <div className="rounded-full bg-primary/10 p-2">
                            {bookmark.icon}
                          </div>
                          <div className="flex-1 space-y-1">
                            <p className="font-medium">{bookmark.title}</p>
                            <p className="text-sm text-muted-foreground">
                              {bookmark.url} • Saved {bookmark.date}
                            </p>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="ghost" size="icon">
                              <IconEdit className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon">
                              <IconTrash className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </TabsContent>
            <TabsContent value="twitter" className="mt-6">
              <div className="grid gap-4">
                {bookmarks
                  .filter((b) => b.source === "twitter")
                  .map((bookmark, index) => (
                    <motion.div
                      key={bookmark.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center space-x-4">
                            <div className="rounded-full bg-primary/10 p-2">
                              {bookmark.icon}
                            </div>
                            <div className="flex-1 space-y-1">
                              <p className="font-medium">{bookmark.title}</p>
                              <p className="text-sm text-muted-foreground">
                                {bookmark.url} • Saved {bookmark.date}
                              </p>
                            </div>
                            <div className="flex space-x-2">
                              <Button variant="ghost" size="icon">
                                <IconEdit className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon">
                                <IconTrash className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
              </div>
            </TabsContent>
            <TabsContent value="google" className="mt-6">
              <div className="grid gap-4">
                {bookmarks
                  .filter((b) => b.source === "google")
                  .map((bookmark, index) => (
                    <motion.div
                      key={bookmark.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center space-x-4">
                            <div className="rounded-full bg-primary/10 p-2">
                              {bookmark.icon}
                            </div>
                            <div className="flex-1 space-y-1">
                              <p className="font-medium">{bookmark.title}</p>
                              <p className="text-sm text-muted-foreground">
                                {bookmark.url} • Saved {bookmark.date}
                              </p>
                            </div>
                            <div className="flex space-x-2">
                              <Button variant="ghost" size="icon">
                                <IconEdit className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon">
                                <IconTrash className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
              </div>
            </TabsContent>
            <TabsContent value="linkedin" className="mt-6">
              <div className="grid gap-4">
                {bookmarks
                  .filter((b) => b.source === "linkedin")
                  .map((bookmark, index) => (
                    <motion.div
                      key={bookmark.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center space-x-4">
                            <div className="rounded-full bg-primary/10 p-2">
                              {bookmark.icon}
                            </div>
                            <div className="flex-1 space-y-1">
                              <p className="font-medium">{bookmark.title}</p>
                              <p className="text-sm text-muted-foreground">
                                {bookmark.url} • Saved {bookmark.date}
                              </p>
                            </div>
                            <div className="flex space-x-2">
                              <Button variant="ghost" size="icon">
                                <IconEdit className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon">
                                <IconTrash className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </MainLayout>
  );
}
