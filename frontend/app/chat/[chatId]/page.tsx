"use client";

import { useChat } from "@ai-sdk/react";
import { Chat } from "@/components/ui/chat";
import { useState } from "react";

interface MessageType {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function Chatbot() {
  const { input, handleInputChange, status, stop } = useChat();
  const isLoading = status === "submitted" || status === "streaming";

  const [messages, setMessages] = useState<MessageType[]>([]);
  const [idCounter, setIdCounter] = useState("");

  const handleSubmit = (
    event?: { preventDefault?: () => void },
    options?: { experimental_attachments?: FileList }
  ) => {
    event?.preventDefault?.();

    const userMessage: MessageType = {
      id: idCounter,
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIdCounter((prev) => prev + 1);

    (async () => {
      try {
        const resp = await fetch("http://localhost:8000/api/chat/id", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input }),
        });

        const data = await resp.json();
        const assistantMessage: MessageType = {
          id: idCounter,
          role: "assistant",
          content: data.response,
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setIdCounter((prev) => prev + 1);
      } catch (err) {
        console.error(err);
      }
    })();
  };

  return (
    <>
      <Chat
        messages={messages}
        input={input}
        handleInputChange={handleInputChange}
        handleSubmit={handleSubmit}
        isGenerating={isLoading}
        stop={stop}
      />
    </>
  );
}
