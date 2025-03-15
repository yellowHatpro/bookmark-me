"use client";

import { MainLayout } from "@/components/layout/main-layout";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
  IconBrandTwitter,
  IconBrandGoogle,
  IconBrandLinkedin,
  IconChartBar,
  IconBookmark,
  IconPlus,
} from "@tabler/icons-react";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <MainLayout>
      <div className="container py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="mb-2 text-3xl font-bold">Dashboard</h1>
          <p className="mb-8 text-muted-foreground">
            Manage your bookmarks and knowledge base
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-3">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Total Bookmarks</CardTitle>
                  <CardDescription>All your saved bookmarks</CardDescription>
                </div>
                <IconBookmark className="h-6 w-6 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">128</div>
                <p className="text-sm text-muted-foreground">
                  +12 from last week
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Connected Services</CardTitle>
                  <CardDescription>Active integrations</CardDescription>
                </div>
                <IconChartBar className="h-6 w-6 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">3</div>
                <div className="mt-2 flex space-x-2">
                  <IconBrandTwitter className="h-5 w-5 text-blue-400" />
                  <IconBrandGoogle className="h-5 w-5 text-red-400" />
                  <IconBrandLinkedin className="h-5 w-5 text-blue-600" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Knowledge Bases</CardTitle>
                  <CardDescription>Your AI-ready collections</CardDescription>
                </div>
                <IconChartBar className="h-6 w-6 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">5</div>
                <p className="text-sm text-muted-foreground">2 updated today</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-8"
        >
          <Tabs defaultValue="recent">
            <div className="flex items-center justify-between">
              <TabsList>
                <TabsTrigger value="recent">Recent Bookmarks</TabsTrigger>
                <TabsTrigger value="collections">Collections</TabsTrigger>
                <TabsTrigger value="knowledge">Knowledge Bases</TabsTrigger>
              </TabsList>
              <Button size="sm">
                <IconPlus className="mr-2 h-4 w-4" />
                Add New
              </Button>
            </div>
            <TabsContent value="recent" className="mt-6">
              <div className="grid gap-4">
                {[...Array(5)].map((_, i) => (
                  <Card key={i}>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-4">
                        <div className="rounded-full bg-primary/10 p-2">
                          <IconBrandTwitter className="h-5 w-5" />
                        </div>
                        <div className="flex-1 space-y-1">
                          <p className="font-medium">
                            How to build a modern web application
                          </p>
                          <p className="text-sm text-muted-foreground">
                            twitter.com • Saved 2 hours ago
                          </p>
                        </div>
                        <Button variant="ghost" size="icon">
                          <IconBookmark className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
            <TabsContent value="collections" className="mt-6">
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="overflow-hidden">
                    <div className="h-32 bg-muted" />
                    <CardHeader>
                      <CardTitle>Development Resources</CardTitle>
                      <CardDescription>
                        {12 + i} bookmarks • Updated 3 days ago
                      </CardDescription>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </TabsContent>
            <TabsContent value="knowledge" className="mt-6">
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[...Array(3)].map((_, i) => (
                  <Card key={i}>
                    <CardHeader>
                      <CardTitle>Web Development</CardTitle>
                      <CardDescription>
                        {24 + i} sources • Last trained 2 days ago
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button className="w-full">Chat with this base</Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </MainLayout>
  );
}
