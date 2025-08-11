"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { useParams } from "next/navigation";

export interface HumanMessageType {
  id: string;
  role: "user";
  content: string;
}
export interface AssistantMessageType {
  id: string;
  role: "assistant";
  content: string;
  retrieved_documents: any[];
}

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<any>([]);

  const { sessionId } = useParams();

  const supabase = createClient();
  const userId = supabase.auth;

  useEffect(() => {
    const fetchMessages = async () => {
      const res = await fetch(
        `http://localhost:8000/api/messages/${sessionId}`
      );
      const data = await res.json();
      setMessages(data.messages);
    };

    fetchMessages();
  }, [sessionId]);

  const handleInputChange = (e: any) => {
    setInput(e.target.value);
  };

  const sendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    setInput("");
    // call api/chat
    //get the session id
    // redirect back to chat/id

    const userMessage: HumanMessageType = {
      id: String(messages.length + 1),
      role: "user",
      content: input,
    };
    setMessages((prev: any) => [...prev, userMessage]);
    setInput("");

    try {
      // Call backend api/chat
      const res = await fetch(`http://localhost:8000/api/chat/${sessionId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userMessage),
      });

      if (!res.ok) {
        throw new Error("Failed to get AI response");
      }

      const data = await res.json();

      // AI response message
      const aiMessage: AssistantMessageType = {
        id: data.id,
        role: data.role,
        content: data.response,
        retrieved_documents: data.retrieved_documents,
      };

      // Append AI message to messages state
      setMessages((prev: any) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error sending chat:", error);
      alert("Failed to send message");
    }
  };

  return (
    <div className="flex flex-col justify-center items-center min-h-screen max-w-xl mx-auto p-4">
      {/* Chat messages box */}
      <div className="w-full border rounded-md p-4 mb-4 h-[500px] overflow-y-auto bg-white">
        {messages.length === 0 && (
          <p className="text-center text-gray-400">Start the conversation!</p>
        )}
        {messages.map((msg: any) => (
          <div
            key={msg.id}
            className={`mb-3 flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                msg.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-900"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      {/* Input form */}
      <form className="flex w-full max-w-sm gap-2" onSubmit={sendChat}>
        <Input
          type="text"
          placeholder="Enter Your Prompt"
          value={input}
          onChange={handleInputChange}
        />
        <Button type="submit" variant="outline">
          <Send />
        </Button>
      </form>
    </div>
  );
}
