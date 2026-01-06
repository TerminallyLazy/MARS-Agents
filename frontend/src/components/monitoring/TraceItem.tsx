import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'
import { formatTimestamp, formatDuration } from '@/lib/utils'
import type { TraceEntry } from '@/stores/agentStore'

interface TraceItemProps {
  trace: TraceEntry
}

export function TraceItem({ trace }: TraceItemProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const eventConfig = {
    start: { icon: 'play_arrow', color: 'text-[var(--color-info)]', bg: 'bg-[var(--color-info)]/10' },
    end: { icon: 'check_circle', color: 'text-[var(--color-success)]', bg: 'bg-[var(--color-success)]/10' },
    error: { icon: 'error', color: 'text-[var(--color-error)]', bg: 'bg-[var(--color-error)]/10' },
    output: { icon: 'output', color: 'text-[var(--accent-secondary)]', bg: 'bg-[var(--accent-secondary)]/10' },
    custom: { icon: 'auto_awesome', color: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning)]/10' },
  }

  const config = eventConfig[trace.event] || eventConfig.custom

  return (
    <div
      className={cn(
        'group flex items-start gap-2 px-3 py-2 rounded-[var(--radius-md)]',
        'hover:bg-[var(--bg-tertiary)] transition-colors duration-[var(--transition-fast)]',
        trace.event === 'start' && 'status-running'
      )}
    >
      <div className={cn('flex-shrink-0 w-6 h-6 rounded flex items-center justify-center', config.bg)}>
        <Icon name={config.icon} size="sm" className={config.color} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--text-subtle)] font-mono">
            {formatTimestamp(trace.timestamp)}
          </span>
          <span className="font-medium text-sm text-[var(--text-default)] truncate">
            {trace.nodeId}
          </span>
          {trace.duration && (
            <span className="text-xs text-[var(--text-muted)]">
              {formatDuration(trace.duration)}
            </span>
          )}
        </div>

        {trace.message && (
          <p className="text-sm text-[var(--text-muted)] mt-0.5 truncate">
            {trace.message}
          </p>
        )}

        {trace.payload && Object.keys(trace.payload).length > 0 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-xs text-[var(--text-subtle)] hover:text-[var(--text-muted)] mt-1"
          >
            <Icon name={isExpanded ? 'expand_less' : 'expand_more'} size="sm" />
            {isExpanded ? 'Hide' : 'Show'} details
          </button>
        )}

        {isExpanded && trace.payload && (
          <pre className="mt-2 p-2 rounded bg-[var(--bg-tertiary)] text-xs font-mono overflow-x-auto">
            {JSON.stringify(trace.payload, null, 2)}
          </pre>
        )}
      </div>
    </div>
  )
}
