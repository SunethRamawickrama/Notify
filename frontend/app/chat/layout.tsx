// app/chat/layout.tsx
import SidebarComponent from "@/components/custom/sidebar";
import React from "react";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden">
      <SidebarComponent />
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
