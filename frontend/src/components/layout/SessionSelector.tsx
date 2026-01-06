import { useState } from 'react'
import { useQuery, useMutation } from 'convex/react'
import { api } from '../../../convex/_generated/api'
import { Button } from '@/components/ui/Button'
import { Icon } from '@/components/ui/Icon'
import { Badge } from '@/components/ui/Badge'
import { cn, formatTimestamp } from '@/lib/utils'
import type { Id } from '../../../convex/_generated/dataModel'

interface SessionSelectorProps {
  currentSessionId: Id<"sessions"> | null
  onSelectSession: (sessionId: Id<"sessions">) => void
  onNewSession: () => void
  className?: string
}

export function SessionSelector({
  currentSessionId,
  onSelectSession,
  onNewSession,
  className,
}: SessionSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const sessions = useQuery(api.sessions.list)
  const deleteSession = useMutation(api.sessions.remove)

  const handleDelete = async (e: React.MouseEvent, sessionId: Id<"sessions">) => {
    e.stopPropagation()
    if (confirm('Delete this session and all its data?')) {
      await deleteSession({ id: sessionId })
    }
  }

  const currentSession = sessions?.find(s => s._id === currentSessionId)

  return (
    <div className={cn('relative', className)}>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2"
      >
        <Icon name="history" size="sm" />
        <span className="max-w-[150px] truncate">
          {currentSession?.name || 'Sessions'}
        </span>
        <Icon name={isOpen ? 'expand_less' : 'expand_more'} size="sm" />
      </Button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full right-0 mt-1 w-80 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-[var(--radius-lg)] shadow-lg z-50 overflow-hidden">
            <div className="p-2 border-b border-[var(--border-default)] flex items-center justify-between">
              <span className="text-sm font-medium text-[var(--text-default)]">
                Research Sessions
              </span>
              <Button variant="primary" size="sm" onClick={() => { onNewSession(); setIsOpen(false); }}>
                <Icon name="add" size="sm" />
                New
              </Button>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {!sessions || sessions.length === 0 ? (
                <div className="p-4 text-center text-[var(--text-muted)] text-sm">
                  No sessions yet. Start a new research task!
                </div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session._id}
                    onClick={() => { onSelectSession(session._id); setIsOpen(false); }}
                    className={cn(
                      'p-3 cursor-pointer hover:bg-[var(--bg-tertiary)] border-b border-[var(--border-default)] last:border-b-0',
                      session._id === currentSessionId && 'bg-[var(--accent-primary)]/10'
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm text-[var(--text-default)] truncate">
                            {session.name}
                          </span>
                          <Badge
                            variant={
                              session.status === 'completed' ? 'success' :
                              session.status === 'error' ? 'error' : 'accent'
                            }
                          >
                            {session.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-[var(--text-muted)] truncate mt-1">
                          {session.task}
                        </p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-[var(--text-subtle)]">
                          <span>{formatTimestamp(new Date(session._creationTime))}</span>
                          <span>Iter {session.iteration}/{session.maxIterations}</span>
                          <Badge variant="default">{session.backend}</Badge>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => handleDelete(e, session._id)}
                        className="text-[var(--text-muted)] hover:text-[var(--color-error)]"
                      >
                        <Icon name="delete" size="sm" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
