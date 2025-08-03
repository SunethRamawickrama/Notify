import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { File } from "lucide-react";

export default function MessageInput() {
  return (
    <div className="flex w-full max-w-sm items-center gap-2">
      <Input type="text" placeholder="Enter Your Prompt" />
      <Button type="submit" variant="outline">
        <File />
      </Button>
    </div>
  );
}
