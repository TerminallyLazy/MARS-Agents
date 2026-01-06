export const GRAPH_NODES = [
  'entry',
  'specialist_agent',
  'refiner',
  'critique',
  'judge',
  'reflection',
  'consensus',
  'meta_learning',
  'memory_evolution',
  'loop_decision',
  'self_healing',
  'diagram',
] as const

export const SPECIALIST_AGENTS = [
  'data_processing',
  'analysis',
  'experimental',
  'learning',
  'optimization',
  'creative',
] as const

export const NODE_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  SUCCESS: 'success',
  ERROR: 'error',
  SKIPPED: 'skipped',
} as const

export const HEALTH_STATUS = {
  HEALTHY: 'healthy',
  DEGRADED: 'degraded',
  CRITICAL: 'critical',
} as const

export const TARGET_SCORE = 8.5
export const MAX_ITERATIONS = 7

export const QUICK_START_TEMPLATES = [
  {
    id: 'agents-md',
    title: 'AGENTS.md Generation',
    description: 'Create comprehensive agent documentation',
    prompt: 'Create an AGENTS.md for a multi-agent research system with recursive self-improvement.',
  },
  {
    id: 'research-synthesis',
    title: 'Research Synthesis',
    description: 'Synthesize research from multiple sources',
    prompt: 'Synthesize research findings on [topic] from multiple academic sources into a cohesive analysis.',
  },
  {
    id: 'analysis-framework',
    title: 'Analysis Framework',
    description: 'Build a structured analysis framework',
    prompt: 'Create a comprehensive analysis framework for evaluating [subject] with clear criteria and metrics.',
  },
] as const

export type GraphNode = typeof GRAPH_NODES[number]
export type SpecialistAgent = typeof SPECIALIST_AGENTS[number]
export type NodeStatus = typeof NODE_STATUS[keyof typeof NODE_STATUS]
export type HealthStatus = typeof HEALTH_STATUS[keyof typeof HEALTH_STATUS]
