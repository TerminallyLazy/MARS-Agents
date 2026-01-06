import { useCallback, useEffect, useRef, useMemo } from 'react'
import { useMutation, useQuery } from 'convex/react'
import { api } from '../../convex/_generated/api'
import { useAgentStore } from '@/stores/agentStore'
import { useSettingsStore } from '@/stores/settingsStore'
import type { Id } from '../../convex/_generated/dataModel'

function debounce<T extends (...args: Parameters<T>) => void>(
  fn: T,
  delay: number
): T & { cancel: () => void } {
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  const debounced = ((...args: Parameters<T>) => {
    if (timeoutId) clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }) as T & { cancel: () => void }
  debounced.cancel = () => {
    if (timeoutId) clearTimeout(timeoutId)
  }
  return debounced
}

export function useConvexSession() {
  const sessionIdRef = useRef<Id<"sessions"> | null>(null)
  
  const createSession = useMutation(api.sessions.create)
  const updateSessionStatus = useMutation(api.sessions.updateStatus)
  const updateSessionIteration = useMutation(api.sessions.updateIteration)
  const updateSessionDraft = useMutation(api.sessions.updateDraft)
  const updateSessionDiagram = useMutation(api.sessions.updateDiagram)
  const updateSessionHealth = useMutation(api.sessions.updateHealth)
  const setSessionBoosted = useMutation(api.sessions.setBoosted)
  
  const addMessage = useMutation(api.messages.add)
  const updateMessageContent = useMutation(api.messages.updateContent)
  const appendMessageContent = useMutation(api.messages.appendContent)
  const updateMessageMetadata = useMutation(api.messages.updateMetadata)
  
  const addTrace = useMutation(api.traces.add)
  
  const sessions = useQuery(api.sessions.list)
  const researchBackend = useSettingsStore((s) => s.researchBackend)
  
  const agentStore = useAgentStore()

  const startSession = useCallback(async (task: string) => {
    const sessionId = await createSession({
      name: task.slice(0, 50) + (task.length > 50 ? '...' : ''),
      task,
      backend: researchBackend,
      maxIterations: agentStore.maxIterations,
    })
    sessionIdRef.current = sessionId
    return sessionId
  }, [createSession, researchBackend, agentStore.maxIterations])

  const endSession = useCallback(async (status: 'completed' | 'error') => {
    if (sessionIdRef.current) {
      await updateSessionStatus({
        id: sessionIdRef.current,
        status,
      })
    }
  }, [updateSessionStatus])

  const persistMessage = useCallback(async (
    role: 'user' | 'assistant' | 'system',
    content: string,
    metadata?: {
      iteration?: number
      score?: number
      previousScore?: number
      nodeId?: string
      isStreaming?: boolean
    }
  ) => {
    if (!sessionIdRef.current) return null
    
    const messageId = await addMessage({
      sessionId: sessionIdRef.current,
      role,
      content,
      ...metadata,
    })
    return messageId
  }, [addMessage])

  const persistTrace = useCallback(async (
    nodeId: string,
    event: 'start' | 'end' | 'error' | 'output' | 'custom',
    message?: string,
    payload?: Record<string, unknown>
  ) => {
    if (!sessionIdRef.current) return null
    
    const traceId = await addTrace({
      sessionId: sessionIdRef.current,
      nodeId,
      event,
      message,
      payload: payload ? JSON.stringify(payload) : undefined,
    })
    return traceId
  }, [addTrace])

  const syncIteration = useCallback(async (iteration: number) => {
    if (sessionIdRef.current) {
      await updateSessionIteration({
        id: sessionIdRef.current,
        iteration,
      })
    }
  }, [updateSessionIteration])

  const syncDraft = useCallback(async (draft: string) => {
    if (sessionIdRef.current) {
      await updateSessionDraft({
        id: sessionIdRef.current,
        currentDraft: draft,
      })
    }
  }, [updateSessionDraft])

  const syncDiagram = useCallback(async (diagram: string) => {
    if (sessionIdRef.current) {
      await updateSessionDiagram({
        id: sessionIdRef.current,
        diagram,
      })
    }
  }, [updateSessionDiagram])

  const syncHealth = useCallback(async (health: 'healthy' | 'degraded' | 'critical') => {
    if (sessionIdRef.current) {
      await updateSessionHealth({
        id: sessionIdRef.current,
        globalHealth: health,
      })
    }
  }, [updateSessionHealth])

  const syncBoosted = useCallback(async (boosted: boolean) => {
    if (sessionIdRef.current) {
      await setSessionBoosted({
        id: sessionIdRef.current,
        isBoosted: boosted,
      })
    }
  }, [setSessionBoosted])

  const debouncedSyncDraft = useMemo(
    () => debounce((draft: string) => syncDraft(draft), 1000),
    [syncDraft]
  )

  const debouncedSyncDiagram = useMemo(
    () => debounce((diagram: string) => syncDiagram(diagram), 500),
    [syncDiagram]
  )

  useEffect(() => {
    let prevIteration = useAgentStore.getState().iteration
    let prevDraft = useAgentStore.getState().currentDraft
    let prevDiagram = useAgentStore.getState().diagram
    let prevHealth = useAgentStore.getState().globalHealth
    let prevBoosted = useAgentStore.getState().isBoosted

    const unsubscribe = useAgentStore.subscribe((state) => {
      if (sessionIdRef.current) {
        if (state.iteration !== prevIteration && state.iteration > 0) {
          prevIteration = state.iteration
          syncIteration(state.iteration)
        }
        if (state.currentDraft !== prevDraft && state.currentDraft) {
          prevDraft = state.currentDraft
          debouncedSyncDraft(state.currentDraft)
        }
        if (state.diagram !== prevDiagram && state.diagram) {
          prevDiagram = state.diagram
          debouncedSyncDiagram(state.diagram)
        }
        if (state.globalHealth !== prevHealth) {
          prevHealth = state.globalHealth
          syncHealth(state.globalHealth)
        }
        if (state.isBoosted !== prevBoosted) {
          prevBoosted = state.isBoosted
          syncBoosted(state.isBoosted)
        }
      }
    })

    return () => {
      unsubscribe()
      debouncedSyncDraft.cancel()
      debouncedSyncDiagram.cancel()
    }
  }, [syncIteration, debouncedSyncDraft, debouncedSyncDiagram, syncHealth, syncBoosted])

  return {
    sessionId: sessionIdRef.current,
    sessions,
    startSession,
    endSession,
    persistMessage,
    persistTrace,
    updateMessageContent,
    appendMessageContent,
    updateMessageMetadata,
  }
}
