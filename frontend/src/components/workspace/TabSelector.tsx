import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'

export type TabId = 'draft' | 'diagram' | 'traces'

interface TabSelectorProps {
  activeTab: TabId
  onTabChange: (tab: TabId) => void
  className?: string
}

const tabs: Array<{ id: TabId; label: string; icon: string }> = [
  { id: 'draft', label: 'Draft', icon: 'description' },
  { id: 'diagram', label: 'Diagram', icon: 'account_tree' },
  { id: 'traces', label: 'Traces', icon: 'timeline' },
]

export function TabSelector({ activeTab, onTabChange, className }: TabSelectorProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-1 p-1 rounded-[var(--radius-md)] bg-[var(--bg-tertiary)]',
        className
      )}
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)]',
            'text-sm font-medium transition-all duration-[var(--transition-fast)]',
            activeTab === tab.id
              ? 'bg-[var(--bg-elevated)] text-[var(--text-loud)] shadow-sm'
              : 'text-[var(--text-muted)] hover:text-[var(--text-default)]'
          )}
        >
          <Icon name={tab.icon} size="sm" />
          {tab.label}
        </button>
      ))}
    </div>
  )
}
