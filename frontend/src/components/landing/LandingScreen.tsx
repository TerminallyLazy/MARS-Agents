import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'
import { InputBar } from './InputBar'
import { QuickActions } from './QuickActions'

interface LandingScreenProps {
  onSubmit: (prompt: string) => void
  className?: string
}

export function LandingScreen({ onSubmit, className }: LandingScreenProps) {
  const [input, setInput] = useState('')

  const handleSubmit = () => {
    if (input.trim()) {
      onSubmit(input.trim())
      setInput('')
    }
  }

  const handleQuickSelect = (prompt: string) => {
    setInput(prompt)
  }

  return (
    <div
      className={cn(
        'min-h-screen flex flex-col items-center justify-center p-8',
        'bg-[var(--bg-primary)]',
        className
      )}
    >
      <div className="w-full max-w-2xl space-y-8">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <div
              className={cn(
              )}
            >
              <img src="/mars-af-logo1.png" alt="Mars Agent Framework" className="w-40 h-40 object-contain" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-[var(--text-loud)] tracking-tight">
            MARS Agent Framework
          </h1>
          <p className="text-lg text-[var(--text-muted)]">
            What would you like to research?
          </p>
        </div>

        <InputBar
          value={input}
          onChange={setInput}
          onSubmit={handleSubmit}
          placeholder="Describe your research task..."
        />

        <div className="space-y-3">
          <p className="text-center text-sm text-[var(--text-subtle)]">
            Quick start with a template
          </p>
          <QuickActions onSelect={handleQuickSelect} />
        </div>

        <div className="flex items-center justify-center gap-6 text-sm text-[var(--text-muted)]">
          <div className="flex items-center gap-1.5">
            <Icon name="memory" size="sm" className="text-[var(--color-success)]" />
            <span>Recursive Self-Improvement</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Icon name="groups" size="sm" className="text-[var(--accent-secondary)]" />
            <span>6 Specialist Agents</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Icon name="psychology" size="sm" className="text-[var(--color-info)]" />
            <span>Constitutional AI</span>
          </div>
        </div>
      </div>
    </div>
  )
}
