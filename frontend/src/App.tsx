import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LandingScreen } from '@/components/landing/LandingScreen'
import { AppShell } from '@/components/layout/AppShell'
import { SplitPane } from '@/components/layout/SplitPane'
import { ChatContainer } from '@/components/chat/ChatContainer'
import { WorkspacePanel } from '@/components/workspace/WorkspacePanel'
import { TracePanel } from '@/components/monitoring/TracePanel'
import { AgentGraph } from '@/components/agent/AgentGraph'
import { ScoreChart } from '@/components/monitoring/ScoreChart'
import { InputBar } from '@/components/landing/InputBar'
import { useAgentStore } from '@/stores/agentStore'
import { useChatStore } from '@/stores/chatStore'
import { useAgentStream } from '@/hooks/useAgentStream'
import { GRAPH_NODES } from '@/lib/constants'

const queryClient = new QueryClient()

type AppView = 'landing' | 'workspace'

function MainApp() {
  const [view, setView] = useState<AppView>('landing')
  const [inputValue, setInputValue] = useState('')

  const {
    isRunning,
    activeNode,
    nodes,
    scores,
    traces,
    currentDraft,
    diagram,
    clearTraces,
  } = useAgentStore()

  const { messages, isStreaming, addMessage } = useChatStore()
  const { startStream } = useAgentStream()

  const handleStartTask = (prompt: string) => {
    addMessage({ role: 'user', content: prompt })
    setView('workspace')
    setInputValue('')
    startStream(prompt)
  }

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      handleStartTask(inputValue.trim())
    }
  }

  const graphNodes = GRAPH_NODES.map((id) => {
    const nodeState = nodes.get(id)
    return {
      id,
      label: id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      status: nodeState?.status || 'pending',
    }
  })

  if (view === 'landing') {
    return <LandingScreen onSubmit={handleStartTask} />
  }

  const leftPanel = (
    <div className="flex flex-col h-full">
      <ChatContainer
        messages={messages}
        isStreaming={isStreaming || isRunning}
        className="flex-1"
      />

      <div className="border-t border-[var(--border-default)] bg-[var(--bg-secondary)]">
        <AgentGraph
          nodes={graphNodes.slice(0, 6)}
          activeNodeId={activeNode || undefined}
        />
        <ScoreChart scores={scores} />
      </div>
    </div>
  )

  const rightPanel = (
    <WorkspacePanel
      draft={currentDraft}
      diagram={diagram}
      traces={<TracePanel traces={traces} onClear={clearTraces} />}
    />
  )

  return (
    <AppShell>
      <div className="flex flex-col h-full">
        <SplitPane left={leftPanel} right={rightPanel} className="flex-1" />

        <div className="p-4 border-t border-[var(--border-default)] bg-[var(--bg-secondary)]">
          <InputBar
            value={inputValue}
            onChange={setInputValue}
            onSubmit={handleSendMessage}
            placeholder="Follow up or refine..."
            disabled={isRunning}
          />
        </div>
      </div>
    </AppShell>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainApp />
    </QueryClientProvider>
  )
}
