import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'
import { Badge } from '@/components/ui/Badge'
import type { NodeStatus } from '@/lib/constants'

interface AgentCardProps {
  agentName: string
  status: NodeStatus | 'boosted'
  confidence?: number
  content?: string
  timestamp?: Date
  className?: string
}

export function AgentCard({
  agentName,
  status,
  confidence,
  content,
  className,
}: AgentCardProps) {
  const statusConfig = {
    pending: {
      variant: 'default' as const,
      icon: 'schedule',
      label: 'Pending',
    },
    running: {
      variant: 'info' as const,
      icon: 'sync',
      label: 'Running',
    },
    success: {
      variant: 'success' as const,
      icon: 'check_circle',
      label: 'Complete',
    },
    error: {
      variant: 'error' as const,
      icon: 'error',
      label: 'Error',
    },
    skipped: {
      variant: 'default' as const,
      icon: 'block',
      label: 'Skipped',
    },
    boosted: {
      variant: 'accent' as const,
      icon: 'bolt',
      label: 'Boosted',
    },
  }

  const config = statusConfig[status]

  return (
    <div
      className={cn(
        'rounded-[var(--radius-lg)] border p-4 space-y-3',
        'bg-[var(--bg-secondary)] border-[var(--border-default)]',
        status === 'running' && 'border-[var(--color-info)] animate-pulse',
        status === 'boosted' && 'border-[var(--accent-secondary)] animate-glow',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className={cn(
              'w-8 h-8 rounded-[var(--radius-md)] flex items-center justify-center',
              'bg-[var(--accent-secondary)]/10'
            )}
          >
            <Icon name="smart_toy" size="sm" className="text-[var(--accent-secondary)]" />
          </div>
          <span className="font-medium text-[var(--text-default)]">{agentName}</span>
        </div>

        <Badge variant={config.variant}>
          <Icon name={config.icon} size="sm" className={status === 'running' ? 'animate-spin' : ''} />
          {config.label}
        </Badge>
      </div>

      {content && (
        <p className="text-sm text-[var(--text-muted)] line-clamp-3">
          {content}
        </p>
      )}

      {confidence !== undefined && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[var(--text-muted)]">Confidence</span>
            <span className="text-[var(--text-default)] font-medium">
              {(confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full h-1.5 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--accent-secondary)] rounded-full transition-all duration-500"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
