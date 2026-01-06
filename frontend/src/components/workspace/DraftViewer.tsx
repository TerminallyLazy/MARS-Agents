import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Icon } from '@/components/ui/Icon'

interface DraftViewerProps {
  content: string
  className?: string
}

export function DraftViewer({ content, className }: DraftViewerProps) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
  }

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'AGENTS.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!content) {
    return (
      <div className={cn('flex flex-col items-center justify-center h-full', className)}>
        <div className="w-12 h-12 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center mb-3">
          <Icon name="edit_document" className="text-[var(--text-muted)]" />
        </div>
        <p className="text-[var(--text-muted)]">
          Document will appear here as it&apos;s generated
        </p>
      </div>
    )
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className="flex-1 overflow-auto p-4">
        <pre className="whitespace-pre-wrap font-mono text-sm text-[var(--text-default)] leading-relaxed">
          {content}
        </pre>
      </div>

      <div className="flex items-center gap-2 p-3 border-t border-[var(--border-default)]">
        <Button variant="secondary" size="sm" onClick={handleCopy}>
          <Icon name="content_copy" size="sm" />
          Copy
        </Button>
        <Button variant="secondary" size="sm" onClick={handleDownload}>
          <Icon name="download" size="sm" />
          Download
        </Button>
      </div>
    </div>
  )
}
