import { useRef, useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Icon } from '@/components/ui/Icon'
import { TraceItem } from './TraceItem'
import type { TraceEntry } from '@/stores/agentStore'

interface TracePanelProps {
  traces: TraceEntry[]
  autoScroll?: boolean
  onClear?: () => void
  className?: string
}

export function TracePanel({
  traces,
  autoScroll: initialAutoScroll = true,
  onClear,
  className,
}: TracePanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = useState(initialAutoScroll)

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [traces, autoScroll])

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className="flex items-center justify-between px-3 py-2 border-b border-[var(--border-default)]">
        <span className="text-sm font-medium text-[var(--text-default)]">
          Trace Log
          <span className="ml-2 text-xs text-[var(--text-muted)]">
            ({traces.length})
          </span>
        </span>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setAutoScroll(!autoScroll)}
            title={autoScroll ? 'Pause auto-scroll' : 'Resume auto-scroll'}
          >
            <Icon name={autoScroll ? 'pause' : 'play_arrow'} size="sm" />
          </Button>
          {onClear && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={onClear}
              title="Clear traces"
            >
              <Icon name="delete" size="sm" />
            </Button>
          )}
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-2 space-y-1">
        {traces.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-8">
            <Icon name="timeline" className="text-[var(--text-muted)] mb-2" />
            <p className="text-sm text-[var(--text-muted)]">
              Trace events will appear here
            </p>
          </div>
        ) : (
          traces.map((trace) => <TraceItem key={trace.id} trace={trace} />)
        )}
      </div>

      <div className="px-3 py-2 border-t border-[var(--border-default)] text-xs text-[var(--text-subtle)]">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={autoScroll}
            onChange={(e) => setAutoScroll(e.target.checked)}
            className="rounded border-[var(--border-default)]"
          />
          Auto-scroll
        </label>
      </div>
    </div>
  )
}
