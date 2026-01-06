import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'
import type { NodeStatus } from '@/lib/constants'

interface AgentNodeProps {
  id: string
  label: string
  status: NodeStatus
  isActive?: boolean
  className?: string
}

export function AgentNode({
  label,
  status,
  isActive = false,
  className,
}: AgentNodeProps) {
  const statusConfig = {
    pending: {
      icon: 'radio_button_unchecked',
      color: 'text-[var(--text-muted)]',
      bg: 'bg-[var(--bg-tertiary)]',
      border: 'border-[var(--border-default)]',
    },
    running: {
      icon: 'play_circle',
      color: 'text-[var(--color-info)]',
      bg: 'bg-[var(--color-info)]/10',
      border: 'border-[var(--color-info)]',
    },
    success: {
      icon: 'check_circle',
      color: 'text-[var(--color-success)]',
      bg: 'bg-[var(--color-success)]/10',
      border: 'border-[var(--color-success)]',
    },
    error: {
      icon: 'error',
      color: 'text-[var(--color-error)]',
      bg: 'bg-[var(--color-error)]/10',
      border: 'border-[var(--color-error)]',
    },
    skipped: {
      icon: 'block',
      color: 'text-[var(--text-subtle)]',
      bg: 'bg-[var(--bg-tertiary)]',
      border: 'border-[var(--border-subtle)]',
    },
  }

  const config = statusConfig[status]

  return (
    <div
      className={cn(
        'flex items-center gap-2 px-3 py-2 rounded-[var(--radius-md)]',
        'border transition-all duration-[var(--transition-fast)]',
        config.bg,
        config.border,
        isActive && 'ring-2 ring-[var(--accent-secondary)] shadow-lg shadow-[var(--accent-secondary)]/20',
        status === 'running' && 'animate-pulse',
        className
      )}
    >
      <Icon name={config.icon} size="sm" className={config.color} />
      <span
        className={cn(
          'text-sm font-medium',
          status === 'pending' || status === 'skipped'
            ? 'text-[var(--text-muted)]'
            : 'text-[var(--text-default)]'
        )}
      >
        {label}
      </span>
    </div>
  )
}
