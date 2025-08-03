import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center h-screen gap-4">
      <img className="h-24 w-auto" src="/logo.png" alt="App Logo" />

      <h1 className="text-3xl font-bold">AI POWERED NOTE TAKING APP</h1>
      <div className="flex gap-4">
        <Link href="auth/login">
          <Button>Login</Button>
        </Link>
        <Link href="auth/sign-up">
          <Button>Sign Up</Button>
        </Link>
      </div>
    </main>
  );
}
