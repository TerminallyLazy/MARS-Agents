import { useState, useRef, useCallback, useEffect, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface SplitPaneProps {
  left: ReactNode
  right: ReactNode
  defaultLeftWidth?: number
  minLeftWidth?: number
  minRightWidth?: number
  className?: string
}

export function SplitPane({
  left,
  right,
  defaultLeftWidth = 40,
  minLeftWidth = 300,
  minRightWidth = 400,
  className,
}: SplitPaneProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [leftWidth, setLeftWidth] = useState(defaultLeftWidth)
  const [isDragging, setIsDragging] = useState(false)

  const handleMouseDown = useCallback(() => {
    setIsDragging(true)
  }, [])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return

      const container = containerRef.current
      const containerRect = container.getBoundingClientRect()
      const containerWidth = containerRect.width

      const newLeftWidth = ((e.clientX - containerRect.left) / containerWidth) * 100

      const minLeftPercent = (minLeftWidth / containerWidth) * 100
      const maxLeftPercent = 100 - (minRightWidth / containerWidth) * 100

      const clampedWidth = Math.max(minLeftPercent, Math.min(maxLeftPercent, newLeftWidth))
      setLeftWidth(clampedWidth)
    },
    [isDragging, minLeftWidth, minRightWidth]
  )

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

  return (
    <div ref={containerRef} className={cn('flex h-full overflow-hidden', className)}>
      <div
        className="h-full overflow-hidden"
        style={{ width: `${leftWidth}%` }}
      >
        {left}
      </div>

      <div
        className={cn(
          'w-1 h-full flex-shrink-0 cursor-col-resize group relative',
          'bg-[var(--border-default)] hover:bg-[var(--accent-secondary)]',
          'transition-colors duration-[var(--transition-fast)]',
          isDragging && 'bg-[var(--accent-secondary)]'
        )}
        onMouseDown={handleMouseDown}
      >
        <div
          className={cn(
            'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
            'w-1 h-8 rounded-full',
            'bg-[var(--border-strong)] group-hover:bg-white',
            'transition-colors duration-[var(--transition-fast)]',
            isDragging && 'bg-white'
          )}
        />
      </div>

      <div
        className="h-full overflow-hidden flex-1"
        style={{ width: `${100 - leftWidth}%` }}
      >
        {right}
      </div>
    </div>
  )
}
