import { useState, useCallback, useRef, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useMutation, useQuery } from 'convex/react'
import { api } from '../convex/_generated/api'
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
import { useSettingsStore } from '@/stores/settingsStore'
import { useAgentStream } from '@/hooks/useAgentStream'
import { GRAPH_NODES } from '@/lib/constants'
import type { Id } from '../convex/_generated/dataModel'

const queryClient = new QueryClient()

type AppView = 'landing' | 'workspace'

function MainApp() {
  const [view, setView] = useState<AppView>('landing')
  const [inputValue, setInputValue] = useState('')
  const sessionIdRef = useRef<Id<"sessions"> | null>(null)

  const createSession = useMutation(api.sessions.create)
  const addConvexMessage = useMutation(api.messages.add)
  const addConvexTrace = useMutation(api.traces.add)
  const convexMessages = useQuery(
    api.messages.listBySession,
    sessionIdRef.current ? { sessionId: sessionIdRef.current } : "skip"
  )
  const convexTraces = useQuery(
    api.traces.listBySession,
    sessionIdRef.current ? { sessionId: sessionIdRef.current } : "skip"
  )

  const {
    isRunning,
    activeNode,
    nodes,
    scores,
    traces,
    currentDraft,
    diagram,
    clearTraces,
    reset: resetAgentStore,
    addTrace,
  } = useAgentStore()

  const { messages, isStreaming, addMessage, clearMessages } = useChatStore()
  const { startStream } = useAgentStream()
  const researchBackend = useSettingsStore((s) => s.researchBackend)

  const persistMessage = useCallback(async (
    role: 'user' | 'assistant' | 'system',
    content: string,
    metadata?: { iteration?: number; score?: number; nodeId?: string; isStreaming?: boolean }
  ) => {
    if (!sessionIdRef.current) return
    await addConvexMessage({
      sessionId: sessionIdRef.current,
      role,
      content,
      ...metadata,
    })
  }, [addConvexMessage])

  const persistTrace = useCallback(async (
    nodeId: string,
    event: 'start' | 'end' | 'error' | 'output' | 'custom',
    message?: string,
    payload?: Record<string, unknown>
  ) => {
    if (!sessionIdRef.current) return
    await addConvexTrace({
      sessionId: sessionIdRef.current,
      nodeId,
      event,
      message,
      payload: payload ? JSON.stringify(payload) : undefined,
    })
  }, [addConvexTrace])

  const traceQueueRef = useRef<typeof traces>([])
  const traceFlushTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const flushTraces = () => {
      if (traceQueueRef.current.length === 0 || !sessionIdRef.current) return
      
      const toFlush = traceQueueRef.current.splice(0, 5)
      toFlush.forEach(trace => {
        persistTrace(trace.nodeId, trace.event, trace.message, trace.payload)
      })
      
      if (traceQueueRef.current.length > 0) {
        traceFlushTimeoutRef.current = setTimeout(flushTraces, 500)
      }
    }

    const unsubscribe = useAgentStore.subscribe((state, prevState) => {
      if (sessionIdRef.current && state.traces.length > prevState.traces.length) {
        const newTraces = state.traces.slice(prevState.traces.length)
        traceQueueRef.current.push(...newTraces)
        
        if (!traceFlushTimeoutRef.current) {
          traceFlushTimeoutRef.current = setTimeout(flushTraces, 300)
        }
      }
    })
    
    return () => {
      unsubscribe()
      if (traceFlushTimeoutRef.current) {
        clearTimeout(traceFlushTimeoutRef.current)
      }
    }
  }, [persistTrace])

  const handleStartTask = useCallback(async (prompt: string) => {
    const sessionId = await createSession({
      name: prompt.slice(0, 50) + (prompt.length > 50 ? '...' : ''),
      task: prompt,
      backend: researchBackend,
      maxIterations: 7,
    })
    sessionIdRef.current = sessionId

    addMessage({ role: 'user', content: prompt })
    await persistMessage('user', prompt)

    setView('workspace')
    setInputValue('')
    startStream(prompt)
  }, [createSession, researchBackend, addMessage, persistMessage, startStream])

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      handleStartTask(inputValue.trim())
    }
  }

  const handleSelectSession = useCallback((sessionId: Id<"sessions">) => {
    sessionIdRef.current = sessionId
    clearMessages()
    resetAgentStore()
    setView('workspace')
  }, [clearMessages, resetAgentStore])

  const handleNewSession = useCallback(() => {
    sessionIdRef.current = null
    clearMessages()
    resetAgentStore()
    setView('landing')
  }, [clearMessages, resetAgentStore])

  useEffect(() => {
    if (convexMessages && sessionIdRef.current) {
      clearMessages()
      convexMessages.forEach(msg => {
        addMessage({
          role: msg.role,
          content: msg.content,
          metadata: {
            iteration: msg.iteration ?? undefined,
            score: msg.score ?? undefined,
            previousScore: msg.previousScore ?? undefined,
            nodeId: msg.nodeId ?? undefined,
            isStreaming: msg.isStreaming ?? undefined,
          }
        })
      })
    }
  }, [convexMessages, addMessage, clearMessages])

  useEffect(() => {
    if (convexTraces && sessionIdRef.current) {
      clearTraces()
      convexTraces.forEach(trace => {
        addTrace({
          nodeId: trace.nodeId,
          event: trace.event,
          timestamp: new Date(trace._creationTime),
          message: trace.message ?? undefined,
          duration: trace.duration ?? undefined,
          payload: trace.payload ? JSON.parse(trace.payload) : undefined,
        })
      })
    }
  }, [convexTraces, addTrace, clearTraces])

  const graphNodes = GRAPH_NODES.map((id) => {
    const nodeState = nodes.get(id)
    return {
      id,
      label: id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      status: nodeState?.status || 'pending',
      currentTask: nodeState?.currentTask,
    }
  })
  
  const isLangGraph = researchBackend === 'langgraph'

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
        {isLangGraph && (
          <AgentGraph
            nodes={graphNodes.slice(0, 6)}
            activeNodeId={activeNode || undefined}
          />
        )}
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
    <AppShell
      currentSessionId={sessionIdRef.current}
      onSelectSession={handleSelectSession}
      onNewSession={handleNewSession}
    >
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
