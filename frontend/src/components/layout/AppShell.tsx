import { type ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { TopBar } from './TopBar'
import type { Id } from '../../../convex/_generated/dataModel'

interface AppShellProps {
  children: ReactNode
  currentSessionId?: Id<"sessions"> | null
  onSelectSession?: (sessionId: Id<"sessions">) => void
  onNewSession?: () => void
  className?: string
}

export function AppShell({ 
  children, 
  currentSessionId,
  onSelectSession,
  onNewSession,
  className 
}: AppShellProps) {
  return (
    <div className={cn('h-screen flex flex-col bg-[var(--bg-primary)]', className)}>
      <TopBar 
        currentSessionId={currentSessionId}
        onSelectSession={onSelectSession}
        onNewSession={onNewSession}
      />
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  )
}
