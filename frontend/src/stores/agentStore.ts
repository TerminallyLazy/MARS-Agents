import { create } from 'zustand'
import type { NodeStatus, HealthStatus, GraphNode } from '@/lib/constants'

export interface TraceEntry {
  id: string
  nodeId: string
  event: 'start' | 'end' | 'error' | 'output' | 'custom'
  timestamp: Date
  duration?: number
  payload?: Record<string, unknown>
  message?: string
}

export interface ReflectionMemory {
  iteration: number
  score: number
  reflection: string
  improvementSuggestion: string
  timestamp: Date
}

export interface AgentOutput {
  agentName: string
  content: string
  confidence: number
}

interface NodeState {
  id: GraphNode
  status: NodeStatus
  startTime?: Date
  endTime?: Date
  output?: unknown
  currentTask?: string
  feedback?: string
}

export interface MetricsState {
  totalTokens: number
  thoughtCount: number
  errorCount: number
  latencyMs: number
  nodesCompleted: number
  nodesTotal: number
}

interface AgentStore {
  isRunning: boolean
  activeNode: GraphNode | null
  nodes: Map<GraphNode, NodeState>
  
  iteration: number
  maxIterations: number
  scores: number[]
  isBoosted: boolean
  
  traces: TraceEntry[]
  maxTraces: number
  
  globalHealth: HealthStatus
  agentHealth: Map<string, { status: HealthStatus; errorCount: number }>
  
  currentDraft: string
  diagram: string
  reflections: ReflectionMemory[]
  agentOutputs: AgentOutput[]
  
  metrics: MetricsState
  startTime: Date | null
  
  setRunning: (running: boolean) => void
  setActiveNode: (node: GraphNode | null) => void
  updateNode: (nodeId: GraphNode, status: NodeStatus, output?: unknown) => void
  setNodeTask: (nodeId: GraphNode, task: string) => void
  setNodeFeedback: (nodeId: GraphNode, feedback: string) => void
  
  setIteration: (iteration: number) => void
  addScore: (score: number) => void
  setBoosted: (boosted: boolean) => void
  
  addTrace: (trace: Omit<TraceEntry, 'id'>) => void
  clearTraces: () => void
  
  setGlobalHealth: (health: HealthStatus) => void
  updateAgentHealth: (agentName: string, status: HealthStatus, errorCount?: number) => void
  
  setCurrentDraft: (draft: string) => void
  setDiagram: (diagram: string) => void
  addReflection: (reflection: ReflectionMemory) => void
  addAgentOutput: (output: AgentOutput) => void
  
  updateMetrics: (updates: Partial<MetricsState>) => void
  incrementErrors: () => void
  
  reset: () => void
}

const initialMetrics: MetricsState = {
  totalTokens: 0,
  thoughtCount: 0,
  errorCount: 0,
  latencyMs: 0,
  nodesCompleted: 0,
  nodesTotal: 12,
}

const initialState = {
  isRunning: false,
  activeNode: null as GraphNode | null,
  nodes: new Map<GraphNode, NodeState>(),
  iteration: 0,
  maxIterations: 7,
  scores: [] as number[],
  isBoosted: false,
  traces: [] as TraceEntry[],
  maxTraces: 500,
  globalHealth: 'healthy' as HealthStatus,
  agentHealth: new Map<string, { status: HealthStatus; errorCount: number }>(),
  currentDraft: '',
  diagram: '',
  reflections: [] as ReflectionMemory[],
  agentOutputs: [] as AgentOutput[],
  metrics: initialMetrics,
  startTime: null as Date | null,
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  ...initialState,
  
  setRunning: (running) => set({ isRunning: running }),
  
  setActiveNode: (node) => set({ activeNode: node }),
  
  updateNode: (nodeId, status, output) => {
    const nodes = new Map(get().nodes)
    const existing = nodes.get(nodeId)
    const now = new Date()
    
    nodes.set(nodeId, {
      id: nodeId,
      status,
      startTime: status === 'running' ? now : existing?.startTime,
      endTime: status !== 'running' && status !== 'pending' ? now : undefined,
      output: output ?? existing?.output,
      currentTask: existing?.currentTask,
      feedback: existing?.feedback,
    })
    
    if (status === 'success' || status === 'error') {
      const completed = Array.from(nodes.values()).filter(
        n => n.status === 'success' || n.status === 'error'
      ).length
      set({ nodes, metrics: { ...get().metrics, nodesCompleted: completed } })
    } else {
      set({ nodes })
    }
  },
  
  setNodeTask: (nodeId, task) => {
    const nodes = new Map(get().nodes)
    const existing = nodes.get(nodeId) || { id: nodeId, status: 'pending' as NodeStatus }
    nodes.set(nodeId, { ...existing, currentTask: task })
    set({ nodes })
  },
  
  setNodeFeedback: (nodeId, feedback) => {
    const nodes = new Map(get().nodes)
    const existing = nodes.get(nodeId) || { id: nodeId, status: 'pending' as NodeStatus }
    nodes.set(nodeId, { ...existing, feedback })
    set({ nodes })
  },
  
  setIteration: (iteration) => set({ iteration }),
  
  addScore: (score) => set((state) => ({ scores: [...state.scores, score] })),
  
  setBoosted: (boosted) => set({ isBoosted: boosted }),
  
  addTrace: (trace) => {
    const id = Math.random().toString(36).substring(2, 9)
    set((state) => {
      const newTraces = [...state.traces, { ...trace, id }]
      if (newTraces.length > state.maxTraces) {
        return { traces: newTraces.slice(-state.maxTraces) }
      }
      return { traces: newTraces }
    })
  },
  
  clearTraces: () => set({ traces: [] }),
  
  setGlobalHealth: (health) => set({ globalHealth: health }),
  
  updateAgentHealth: (agentName, status, errorCount = 0) => {
    const agentHealth = new Map(get().agentHealth)
    agentHealth.set(agentName, { status, errorCount })
    set({ agentHealth })
  },
  
  setCurrentDraft: (draft) => set({ currentDraft: draft }),
  
  setDiagram: (diagram) => set({ diagram }),
  
  addReflection: (reflection) => set((state) => ({
    reflections: [...state.reflections, reflection],
  })),
  
  addAgentOutput: (output) => set((state) => ({
    agentOutputs: [...state.agentOutputs, output],
  })),
  
  updateMetrics: (updates) => set((state) => ({
    metrics: { ...state.metrics, ...updates },
  })),
  
  incrementErrors: () => set((state) => ({
    metrics: { ...state.metrics, errorCount: state.metrics.errorCount + 1 },
  })),
  
  reset: () => set({
    ...initialState,
    nodes: new Map(),
    agentHealth: new Map(),
    metrics: { ...initialMetrics },
    startTime: new Date(),
  }),
}))
