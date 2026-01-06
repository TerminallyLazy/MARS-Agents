import { cn } from '@/lib/utils'
import { AgentNode } from './AgentNode'
import type { NodeStatus } from '@/lib/constants'

interface GraphNodeData {
  id: string
  label: string
  status: NodeStatus
  currentTask?: string
}

interface AgentGraphProps {
  nodes: GraphNodeData[]
  activeNodeId?: string
  className?: string
}

export function AgentGraph({ nodes, activeNodeId, className }: AgentGraphProps) {
  return (
    <div className={cn('p-4', className)}>
      <h3 className="text-sm font-medium text-[var(--text-default)] mb-4">
        Agent Graph
      </h3>

      <div className="relative space-y-2">
        {nodes.map((node, index) => (
          <div key={node.id} className="relative">
            {index < nodes.length - 1 && (
              <div
                className={cn(
                  'absolute left-5 top-full w-0.5 h-2 -translate-x-1/2',
                  'bg-[var(--border-strong)]'
                )}
              />
            )}
            <AgentNode
              id={node.id}
              label={node.label}
              status={node.status}
              isActive={node.id === activeNodeId}
              currentTask={node.currentTask}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
