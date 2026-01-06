import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'
import { QUICK_START_TEMPLATES } from '@/lib/constants'

interface QuickActionsProps {
  onSelect: (prompt: string) => void
  className?: string
}

export function QuickActions({ onSelect, className }: QuickActionsProps) {
  return (
    <div className={cn('flex flex-wrap justify-center gap-3', className)}>
      {QUICK_START_TEMPLATES.map((template) => (
        <button
          key={template.id}
          onClick={() => onSelect(template.prompt)}
          className={cn(
            'group flex items-center gap-2 px-4 py-2.5 rounded-[var(--radius-lg)]',
            'bg-[var(--bg-secondary)] border border-[var(--border-default)]',
            'hover:bg-[var(--bg-tertiary)] hover:border-[var(--border-strong)]',
            'transition-all duration-[var(--transition-fast)]',
            'text-left'
          )}
        >
          <div
            className={cn(
              'flex items-center justify-center w-8 h-8 rounded-[var(--radius-md)]',
              'bg-[var(--accent-secondary)]/10 text-[var(--accent-secondary)]',
              'group-hover:bg-[var(--accent-secondary)]/20'
            )}
          >
            <Icon
              name={
                template.id === 'agents-md'
                  ? 'description'
                  : template.id === 'research-synthesis'
                  ? 'biotech'
                  : 'analytics'
              }
              size="sm"
            />
          </div>
          <div>
            <div className="font-medium text-sm text-[var(--text-default)]">
              {template.title}
            </div>
            <div className="text-xs text-[var(--text-muted)]">
              {template.description}
            </div>
          </div>
        </button>
      ))}
    </div>
  )
}
