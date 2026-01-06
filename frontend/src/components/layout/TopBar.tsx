import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Icon } from '@/components/ui/Icon'
import { useSettingsStore } from '@/stores/settingsStore'
import { useAgentStore } from '@/stores/agentStore'

interface TopBarProps {
  onMenuClick?: () => void
  className?: string
}

export function TopBar({ onMenuClick, className }: TopBarProps) {
  const { theme, setTheme, getResolvedTheme, researchBackend, setResearchBackend } = useSettingsStore()
  const globalHealth = useAgentStore((s) => s.globalHealth)

  const toggleBackend = () => {
    setResearchBackend(researchBackend === 'langgraph' ? 'gemini' : 'langgraph')
  }

  const resolvedTheme = getResolvedTheme()

  const cycleTheme = () => {
    const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system']
    const currentIndex = themes.indexOf(theme)
    setTheme(themes[(currentIndex + 1) % themes.length])
  }

  const healthVariant = {
    healthy: 'success',
    degraded: 'warning',
    critical: 'error',
  } as const

  const healthIcon = {
    healthy: 'check_circle',
    degraded: 'warning',
    critical: 'error',
  } as const

  return (
    <header
      className={cn(
        'h-14 flex items-center justify-between px-4',
        'border-b border-[var(--border-default)] bg-[var(--bg-secondary)]',
        className
      )}
    >
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={onMenuClick}>
          <Icon name="menu" />
        </Button>
        <div className="flex items-center gap-2">
          <div
            className={cn(
              'flex items-center justify-center w-8 h-8 rounded-lg',
              'bg-gradient-to-br from-[var(--accent-secondary)] to-[var(--accent-deep)]'
            )}
          >
            <Icon name="smart_toy" size="sm" className="text-white" />
          </div>
          <span className="font-semibold text-[var(--text-loud)]">
            MARS Agent Framework
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleBackend}
          title={`Switch to ${researchBackend === 'gemini' ? 'LangGraph' : 'Gemini'}`}
          className="flex items-center gap-1.5 px-2"
        >
          <Icon name={researchBackend === 'gemini' ? 'science' : 'account_tree'} size="sm" />
          <span className="text-xs font-medium">
            {researchBackend === 'gemini' ? 'Gemini' : 'LangGraph'}
          </span>
        </Button>

        <Badge variant={healthVariant[globalHealth]}>
          <Icon name={healthIcon[globalHealth]} size="sm" />
          {globalHealth.charAt(0).toUpperCase() + globalHealth.slice(1)}
        </Badge>

        <Button variant="ghost" size="icon" onClick={cycleTheme} title={`Theme: ${theme}`}>
          <Icon name={resolvedTheme === 'dark' ? 'dark_mode' : 'light_mode'} />
        </Button>

        <Button variant="ghost" size="icon">
          <Icon name="settings" />
        </Button>

        <Button variant="ghost" size="icon">
          <Icon name="help_outline" />
        </Button>
      </div>
    </header>
  )
}
