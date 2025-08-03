import Link from "next/link";

import { AuthButton } from "../auth-button";
import { hasEnvVars } from "@/lib/utils";
import { EnvVarWarning } from "../env-var-warning";

export default function Navbar() {
  return (
    <header className="shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 p-3">
        <Link href="/" className="flex items-center gap-2">
          <img
            src="/logo.png"
            alt="Notify Logo"
            className="h-14 w-14 rounded-sm"
          />
          <span className="text-xl font-bold tracking-tight">Notify</span>
        </Link>

        <nav>
          <ul className=" mx-auto max-w-7xl flex items-center px-4 pr-20 py-4 gap-6 text-sm font-medium text-gray-700 dark:text-gray-200">
            <li>
              <Link href="/upload">Upload</Link>
            </li>
            <li>
              <Link href="/">Courses</Link>
            </li>
            <li>
              <Link href="/">Schedule</Link>
            </li>
            <li>
              <Link href="/">Campus Tool</Link>
            </li>
            {!hasEnvVars ? <EnvVarWarning /> : <AuthButton />}
          </ul>
        </nav>
      </div>
    </header>
  );
}
