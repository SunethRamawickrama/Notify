"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "../ui/button";
import { Menu, MessageSquare } from "lucide-react";
import { ScrollArea } from "../ui/scroll-area";
import Link from "next/link";

export default function SidebarComponent() {
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);
  const [sessions, setSessions] = useState<any[]>([]);

  useEffect(() => {
    let socket: WebSocket;

    async function init() {
      try {
        // Initial fetch
        const res = await fetch("http://localhost:8000/api/sessions", {
          headers: {
            "Content-Type": "application/json",
            userId: "demo-user",
          },
        });
        const data = await res.json();
        setSessions(data.sessions);

        // WebSocket for realtime updates
        socket = new WebSocket("ws://localhost:8000/ws/sessions");

        socket.onmessage = (event) => {
          const msg = JSON.parse(event.data);
          if (msg.type === "new_session") {
            setSessions((prev) => [msg.data, ...prev]);
          }
        };

        socket.onopen = () => console.log("✅ WebSocket connected");
        socket.onerror = (err) => console.error("❌ WebSocket error:", err);
        socket.onclose = () => console.log("ℹ️ WebSocket closed");
      } catch (error) {
        console.error("Error fetching sessions:", error);
      } finally {
        setLoading(false);
      }
    }

    init();

    return () => {
      if (socket) socket.close();
    };
  }, []);

  return (
    <div
      className={cn(
        "h-screen bg-muted border-r transition-all duration-300 ease-in-out flex flex-col",
        collapsed ? "w-[60px]" : "w-[280px]"
      )}
    >
      {/* Top Bar */}
      <div className="flex items-center justify-between p-4 border-b">
        {!collapsed && (
          <Link href="/chat">
            <Button className="ml-2" variant="default">
              + New Chat
            </Button>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
        >
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      {/* Chat History List */}
      <ScrollArea className="flex-1">
        <ul className="p-2 space-y-1">
          {loading ? (
            <li className="px-3 py-2 text-sm text-muted-foreground">
              Loading...
            </li>
          ) : sessions.length === 0 ? (
            <li className="px-3 py-2 text-sm text-muted-foreground">
              No chats found
            </li>
          ) : (
            sessions.map((chat) => (
              <li
                key={chat.sessionId}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent cursor-pointer"
              >
                <MessageSquare className="h-4 w-4" />
                {!collapsed && (
                  <Link href={`/chat/${chat.sessionId}`}>
                    <span className="truncate">{chat.title || "New chat"}</span>
                  </Link>
                )}
              </li>
            ))
          )}
        </ul>
      </ScrollArea>
    </div>
  );
}
