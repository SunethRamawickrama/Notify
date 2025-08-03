"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

export default function Chat() {
  const [input, setInput] = useState("");

  const handleInputChange = (e: any) => {
    setInput(e.target.value);
  };

  const sendChat = () => {
    setInput("");
  };

  return (
    <div className="flex justify-center items-center min-h-screen">
      <form>
        <div className="flex w-full max-w-sm items-center gap-2">
          <Input
            onSubmit={sendChat}
            onChange={handleInputChange}
            type="text"
            placeholder="Enter Your Prompt"
          />
          <Button onClick={sendChat} type="submit" variant="outline">
            <Send />
          </Button>
        </div>
      </form>
    </div>
  );
}
