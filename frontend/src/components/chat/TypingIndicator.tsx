import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'

interface TypingIndicatorProps {
  message?: string
  className?: string
}

export function TypingIndicator({
  message = 'Thinking...',
  className,
}: TypingIndicatorProps) {
  return (
    <div className={cn('flex gap-3', className)}>
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          'bg-[var(--color-success)]/20 text-[var(--color-success)]'
        )}
      >
        <Icon name="smart_toy" size="sm" />
      </div>

      <div
        className={cn(
          'rounded-[var(--radius-lg)] px-4 py-3',
          'bg-[var(--bg-secondary)] border border-[var(--border-default)]'
        )}
      >
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <span
              className="w-2 h-2 rounded-full bg-[var(--text-muted)] animate-bounce"
              style={{ animationDelay: '0ms' }}
            />
            <span
              className="w-2 h-2 rounded-full bg-[var(--text-muted)] animate-bounce"
              style={{ animationDelay: '150ms' }}
            />
            <span
              className="w-2 h-2 rounded-full bg-[var(--text-muted)] animate-bounce"
              style={{ animationDelay: '300ms' }}
            />
          </div>
          <span className="text-sm text-[var(--text-muted)]">{message}</span>
        </div>
      </div>
    </div>
  )
}
