import type { Metadata } from "next";
import { Providers } from "./providers";
import { Sidebar } from "@/components/sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vigil - AI Agent Observability",
  description: "Monitor and debug AI agent pipelines",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div className="flex h-screen">
            <Sidebar />
            <main className="flex-1 overflow-auto p-6">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
