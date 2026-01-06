import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Icon } from '@/components/ui/Icon'
import { SessionSelector } from './SessionSelector'
import { useSettingsStore } from '@/stores/settingsStore'
import { useAgentStore } from '@/stores/agentStore'
import type { Id } from '../../../convex/_generated/dataModel'

interface TopBarProps {
  onMenuClick?: () => void
  currentSessionId?: Id<"sessions"> | null
  onSelectSession?: (sessionId: Id<"sessions">) => void
  onNewSession?: () => void
  className?: string
}

export function TopBar({ 
  onMenuClick, 
  currentSessionId,
  onSelectSession,
  onNewSession,
  className 
}: TopBarProps) {
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
          <img
            src="/mars-af-logo1.svg"
            alt="MARS"
            className="w-8 h-8"
          />
          <span className="font-semibold text-[var(--text-loud)]">
            MARS Agent Framework
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {onSelectSession && onNewSession && (
          <SessionSelector
            currentSessionId={currentSessionId ?? null}
            onSelectSession={onSelectSession}
            onNewSession={onNewSession}
          />
        )}

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
