import { type ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { TopBar } from './TopBar'

interface AppShellProps {
  children: ReactNode
  className?: string
}

export function AppShell({ children, className }: AppShellProps) {
  return (
    <div className={cn('h-screen flex flex-col bg-[var(--bg-primary)]', className)}>
      <TopBar />
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  )
}
