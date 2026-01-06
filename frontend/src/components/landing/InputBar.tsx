import { useRef, useEffect, type KeyboardEvent } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Icon } from '@/components/ui/Icon'

interface InputBarProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export function InputBar({
  value,
  onChange,
  onSubmit,
  placeholder = 'Describe your research task...',
  disabled = false,
  className,
}: InputBarProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [value])

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault()
      if (value.trim() && !disabled) {
        onSubmit()
      }
    }
  }

  return (
    <div
      className={cn(
        'rounded-[var(--radius-xl)] border border-[var(--border-default)] bg-[var(--bg-elevated)] shadow-lg',
        'focus-within:border-[var(--accent-secondary)] focus-within:ring-2 focus-within:ring-[var(--accent-secondary)]/20',
        'transition-all duration-[var(--transition-base)]',
        className
      )}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={3}
        className={cn(
          'w-full resize-none bg-transparent px-4 pt-4 pb-2 text-[var(--text-default)]',
          'placeholder:text-[var(--text-subtle)] focus:outline-none',
          'text-base leading-relaxed',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      />
      
      <div className="flex items-center justify-end px-3 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--text-subtle)]">
            {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}+Enter to send
          </span>
          <Button
            variant="primary"
            size="sm"
            onClick={onSubmit}
            disabled={disabled || !value.trim()}
          >
            <Icon name="send" size="sm" />
            Send
          </Button>
        </div>
      </div>
    </div>
  )
}
