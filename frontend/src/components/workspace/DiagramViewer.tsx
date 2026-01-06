import { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Icon } from '@/components/ui/Icon'

interface DiagramViewerProps {
  code: string
  className?: string
}

function extractMermaidCode(raw: string): string {
  const fencePattern = /^```(?:mermaid)?\s*\n?([\s\S]*?)\n?```$/
  const match = raw.trim().match(fencePattern)
  return match ? match[1].trim() : raw.trim()
}

export function DiagramViewer({ code, className }: DiagramViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const diagramIdRef = useRef(0)

  useEffect(() => {
    if (!code || !containerRef.current) return

    const renderDiagram = async () => {
      try {
        const mermaid = (await import('mermaid')).default
        mermaid.initialize({
          startOnLoad: false,
          theme: document.documentElement.classList.contains('dark') ? 'dark' : 'default',
          fontFamily: 'var(--font-sans)',
        })

        const cleanCode = extractMermaidCode(code)
        diagramIdRef.current += 1
        const { svg } = await mermaid.render(`mermaid-diagram-${diagramIdRef.current}`, cleanCode)
        if (containerRef.current) {
          containerRef.current.innerHTML = svg
        }
      } catch (error) {
        console.error('Mermaid rendering error:', error)
        if (containerRef.current) {
          containerRef.current.innerHTML = `<pre class="text-[var(--color-error)]">Error rendering diagram</pre>`
        }
      }
    }

    renderDiagram()
  }, [code])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
  }

  if (!code) {
    return (
      <div className={cn('flex flex-col items-center justify-center h-full', className)}>
        <div className="w-12 h-12 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center mb-3">
          <Icon name="account_tree" className="text-[var(--text-muted)]" />
        </div>
        <p className="text-[var(--text-muted)]">
          Diagram will appear here when generated
        </p>
      </div>
    )
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4 flex items-center justify-center bg-[var(--bg-secondary)]"
      />

      <div className="flex items-center gap-2 p-3 border-t border-[var(--border-default)]">
        <Button variant="secondary" size="sm" onClick={handleCopy}>
          <Icon name="content_copy" size="sm" />
          Copy Code
        </Button>
      </div>
    </div>
  )
}
