"use client";

import { useState } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
  IconSend,
  IconMessageChatbot,
  IconDatabase,
  IconBrandTwitter,
  IconBrandGoogle,
  IconBrandLinkedin,
} from "@tabler/icons-react";
import { Button } from "@/components/ui/button";

// Mock data for knowledge bases
const knowledgeBases = [
  {
    id: 1,
    name: "Web Development",
    sources: 24,
    lastTrained: "2 days ago",
    icon: <IconDatabase className="h-5 w-5" />,
  },
  {
    id: 2,
    name: "AI Research",
    sources: 18,
    lastTrained: "1 week ago",
    icon: <IconDatabase className="h-5 w-5" />,
  },
  {
    id: 3,
    name: "Productivity Tips",
    sources: 12,
    lastTrained: "3 days ago",
    icon: <IconDatabase className="h-5 w-5" />,
  },
];

// Mock data for chat messages
const initialMessages = [
  {
    id: 1,
    content: "Hello! How can I help you with your knowledge base today?",
    sender: "ai",
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
];

export default function ChatPage() {
  const [activeBase, setActiveBase] = useState(knowledgeBases[0]);
  const [messages, setMessages] = useState(initialMessages);
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      content: inputValue,
      sender: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    // Simulate AI response after a short delay
    setTimeout(() => {
      const aiMessage = {
        id: messages.length + 2,
        content: `I found some information about "${inputValue}" in your ${activeBase.name} knowledge base. Here's what I found...`,
        sender: "ai",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1000);
  };

  return (
    <MainLayout>
      <div className="container py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="mb-2 text-3xl font-bold">Chat with Your Knowledge</h1>
          <p className="text-muted-foreground">
            Ask questions and get answers from your personal knowledge base
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-3">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="md:col-span-1"
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Knowledge Bases</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="bases" className="h-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="bases">Bases</TabsTrigger>
                    <TabsTrigger value="sources">Sources</TabsTrigger>
                  </TabsList>
                  <TabsContent value="bases" className="mt-4 space-y-4">
                    {knowledgeBases.map((base) => (
                      <div
                        key={base.id}
                        className={`flex cursor-pointer items-center space-x-3 rounded-md p-3 transition-colors hover:bg-muted ${
                          activeBase.id === base.id ? "bg-muted" : ""
                        }`}
                        onClick={() => setActiveBase(base)}
                      >
                        <div className="rounded-full bg-primary/10 p-2">
                          {base.icon}
                        </div>
                        <div>
                          <p className="font-medium">{base.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {base.sources} sources • Last trained{" "}
                            {base.lastTrained}
                          </p>
                        </div>
                      </div>
                    ))}
                  </TabsContent>
                  <TabsContent value="sources" className="mt-4 space-y-4">
                    <div className="flex cursor-pointer items-center space-x-3 rounded-md p-3 transition-colors hover:bg-muted">
                      <div className="rounded-full bg-primary/10 p-2">
                        <IconBrandTwitter className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium">Twitter</p>
                        <p className="text-sm text-muted-foreground">
                          42 bookmarks
                        </p>
                      </div>
                    </div>
                    <div className="flex cursor-pointer items-center space-x-3 rounded-md p-3 transition-colors hover:bg-muted">
                      <div className="rounded-full bg-primary/10 p-2">
                        <IconBrandGoogle className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium">Google Keep</p>
                        <p className="text-sm text-muted-foreground">
                          28 bookmarks
                        </p>
                      </div>
                    </div>
                    <div className="flex cursor-pointer items-center space-x-3 rounded-md p-3 transition-colors hover:bg-muted">
                      <div className="rounded-full bg-primary/10 p-2">
                        <IconBrandLinkedin className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium">LinkedIn</p>
                        <p className="text-sm text-muted-foreground">
                          15 bookmarks
                        </p>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="md:col-span-2"
          >
            <Card className="flex h-[600px] flex-col">
              <CardHeader className="border-b">
                <div className="flex items-center space-x-3">
                  <div className="rounded-full bg-primary/10 p-2">
                    <IconMessageChatbot className="h-5 w-5" />
                  </div>
                  <CardTitle>Chatting with {activeBase.name}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${
                        message.sender === "user"
                          ? "justify-end"
                          : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.sender === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                      >
                        <p>{message.content}</p>
                        <p
                          className={`mt-1 text-xs ${
                            message.sender === "user"
                              ? "text-primary-foreground/70"
                              : "text-muted-foreground"
                          }`}
                        >
                          {new Date(message.timestamp).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
              <div className="border-t p-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Ask a question about your knowledge base..."
                    className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleSendMessage();
                      }
                    }}
                  />
                  <Button onClick={handleSendMessage}>
                    <IconSend className="h-4 w-4" />
                    <span className="sr-only">Send</span>
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </MainLayout>
  );
}
