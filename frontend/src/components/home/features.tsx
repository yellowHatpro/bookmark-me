"use client";

import { motion } from "framer-motion";
import {
  IconBrandTwitter,
  IconBrandGoogle,
  IconBrandLinkedin,
  IconBookmark,
  IconMessageChatbot,
  IconDatabase,
} from "@tabler/icons-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const features = [
  {
    icon: <IconBrandTwitter className="h-10 w-10" />,
    title: "Twitter Integration",
    description:
      "Connect your Twitter account to save and organize your favorite tweets.",
  },
  {
    icon: <IconBrandGoogle className="h-10 w-10" />,
    title: "Google Keep Integration",
    description: "Import your notes and bookmarks from Google Keep.",
  },
  {
    icon: <IconBrandLinkedin className="h-10 w-10" />,
    title: "LinkedIn Integration",
    description: "Save articles and posts from your LinkedIn feed.",
  },
  {
    icon: <IconBookmark className="h-10 w-10" />,
    title: "Bookmark Organization",
    description: "Organize your bookmarks into collections and categories.",
  },
  {
    icon: <IconDatabase className="h-10 w-10" />,
    title: "Knowledge Base",
    description: "Create a personal knowledge base from your bookmarks.",
  },
  {
    icon: <IconMessageChatbot className="h-10 w-10" />,
    title: "AI Chat",
    description: "Chat with your knowledge base using advanced AI.",
  },
];

export function Features() {
  return (
    <section id="features" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-[58rem] text-center">
          <h2 className="mb-6 text-3xl font-bold sm:text-4xl md:text-5xl">
            All Your Bookmarks in One Place
          </h2>
          <p className="mb-12 text-xl text-muted-foreground">
            Bookmark Me connects to your favorite services and helps you
            organize and interact with your saved content.
          </p>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full">
                <CardHeader>
                  <div className="mb-4 rounded-full bg-primary/10 p-3 w-fit">
                    {feature.icon}
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
