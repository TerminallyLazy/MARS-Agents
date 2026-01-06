import { useState, type ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { TabSelector, type TabId } from './TabSelector'
import { DraftViewer } from './DraftViewer'
import { DiagramViewer } from './DiagramViewer'

interface WorkspacePanelProps {
  draft: string
  diagram: string
  traces: ReactNode
  className?: string
}

export function WorkspacePanel({
  draft,
  diagram,
  traces,
  className,
}: WorkspacePanelProps) {
  const [activeTab, setActiveTab] = useState<TabId>('draft')

  return (
    <div className={cn('flex flex-col h-full bg-[var(--bg-primary)]', className)}>
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-default)]">
        <h2 className="font-semibold text-[var(--text-loud)]">Workspace</h2>
        <TabSelector activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="flex-1 overflow-hidden">
        {activeTab === 'draft' && <DraftViewer content={draft} />}
        {activeTab === 'diagram' && <DiagramViewer code={diagram} />}
        {activeTab === 'traces' && (
          <div className="h-full overflow-auto">{traces}</div>
        )}
      </div>
    </div>
  )
}
