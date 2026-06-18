import type { ReactNode } from "react"
import { Sidebar } from "./Sidebar"

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background text-text-primary font-sans flex">
      <Sidebar />
      <main className="flex-1 ml-64 p-8 relative">
        <div className="max-w-[1400px] mx-auto relative z-10">
          {children}
        </div>
      </main>
    </div>
  )
}
