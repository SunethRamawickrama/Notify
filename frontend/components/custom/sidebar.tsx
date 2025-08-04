"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "../ui/button";
import { Menu, MessageSquare } from "lucide-react";
import { ScrollArea } from "../ui/scroll-area";

const mockChats = [
  { id: 1, title: "Chat with Alice" },
  { id: 2, title: "Meeting Notes" },
  { id: 3, title: "Research Ideas" },
  { id: 4, title: "GPT Testing" },
  { id: 5, title: "UI Feedback" },
];

export default function SidebarComponent() {
  const [collapsed, setCollapsed] = useState(false);

  //if there is an addition to the session in the database, this should auto update the sidebar
  const [chats, setChats] = useState(mockChats);

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
          <Button className=" ml-2" variant="default">
            + New Chat
          </Button>
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
          {chats.map((chat) => (
            <li
              key={chat.id}
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent cursor-pointer"
            >
              <MessageSquare className="h-4 w-4" />
              {!collapsed && <span className="truncate">{chat.title}</span>}
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}
