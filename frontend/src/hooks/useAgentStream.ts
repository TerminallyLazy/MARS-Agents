import { useCallback, useRef } from 'react'
import { useAgentStore } from '@/stores/agentStore'
import { useChatStore } from '@/stores/chatStore'
import { useSettingsStore } from '@/stores/settingsStore'
import type { GraphNode } from '@/lib/constants'

interface StreamEvent {
  event: string
  data: Record<string, unknown>
  timestamp: string
}

export function useAgentStream() {
  const abortControllerRef = useRef<AbortController | null>(null)

  const {
    setRunning,
    setActiveNode,
    updateNode,
    addTrace,
    addScore,
    setBoosted,
    setCurrentDraft,
    setDiagram,
    setGlobalHealth,
    setIteration,
    reset: resetAgentStore,
  } = useAgentStore()

  const { addMessage, updateMessage, setStreaming, appendToMessage } = useChatStore()
  const researchBackend = useSettingsStore((s) => s.researchBackend)

  const startStream = useCallback(
    async (task: string): Promise<() => void> => {
      resetAgentStore()
      setRunning(true)

      const messageId = addMessage({
        role: 'assistant',
        content: '',
        metadata: { isStreaming: true, iteration: 1 },
      })
      setStreaming(true, messageId)

      abortControllerRef.current = new AbortController()

      const endpoint = researchBackend === 'gemini' 
        ? '/api/research/gemini/stream' 
        : '/api/runs/stream'

      addTrace({
        nodeId: 'system',
        event: 'custom',
        timestamp: new Date(),
        message: `Using ${researchBackend === 'gemini' ? 'Gemini Deep Research' : 'LangGraph'} backend`,
      })

      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task }),
          signal: abortControllerRef.current.signal,
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }

        const reader = response.body?.getReader()
        if (!reader) throw new Error('No response body')

        const decoder = new TextDecoder()
        let buffer = ''

        const processStream = async () => {
          try {
            while (true) {
              const { done, value } = await reader.read()
              if (done) break

              buffer += decoder.decode(value, { stream: true })
              const lines = buffer.split('\n')
              buffer = lines.pop() || ''

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const event: StreamEvent = JSON.parse(line.slice(6))
                    handleEvent(event, messageId)
                  } catch (e) {
                    console.warn('Failed to parse SSE event:', line, e)
                  }
                }
              }
            }
          } finally {
            setRunning(false)
            setStreaming(false)
            setActiveNode(null)
          }
        }

        await processStream()
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          updateMessage(messageId, 'Research cancelled.')
        } else {
          console.error('Stream error:', error)
          updateMessage(
            messageId, 
            `Error connecting to ${researchBackend} backend: ${error instanceof Error ? error.message : 'Unknown error'}\n\nMake sure the backend server is running.`
          )
        }
        setRunning(false)
        setStreaming(false)
        setGlobalHealth('critical')
      }

      return () => {
        abortControllerRef.current?.abort()
        setRunning(false)
        setStreaming(false)
      }
    },
    [resetAgentStore, setRunning, addMessage, setStreaming, updateMessage, setActiveNode, researchBackend, addTrace, setGlobalHealth]
  )

  const handleEvent = useCallback(
    (event: StreamEvent, messageId: string) => {
      const { event: eventType, data } = event

      switch (eventType) {
        case 'run_start':
          addTrace({
            nodeId: 'system',
            event: 'custom',
            timestamp: new Date(),
            message: `Starting research: ${data.task || 'task'}`,
          })
          break

        case 'node_start': {
          const nodeName = data.name as GraphNode
          if (nodeName) {
            setActiveNode(nodeName)
            updateNode(nodeName, 'running')
            addTrace({
              nodeId: nodeName,
              event: 'start',
              timestamp: new Date(),
              message: `${nodeName} started`,
            })
          }
          break
        }

        case 'node_end': {
          const nodeName = data.name as GraphNode
          if (nodeName) {
            updateNode(nodeName, 'success', data.output)

            const output = data.output as Record<string, unknown> | undefined
            if (output) {
              if (output.scores && Array.isArray(output.scores)) {
                const latestScore = output.scores[output.scores.length - 1]
                if (typeof latestScore === 'number') {
                  addScore(latestScore)
                }
              }

              if (output.iteration && typeof output.iteration === 'number') {
                setIteration(output.iteration)
              }

              if (output.current_draft && typeof output.current_draft === 'string') {
                setCurrentDraft(output.current_draft)
              }

              if (output.diagram && typeof output.diagram === 'string') {
                setDiagram(output.diagram)
              }

              if (output.is_boosted === true) {
                setBoosted(true)
                addTrace({
                  nodeId: 'system',
                  event: 'custom',
                  timestamp: new Date(),
                  message: 'RECURSIVE BOOST ACTIVATED',
                })
              }
            }

            addTrace({
              nodeId: nodeName,
              event: 'end',
              timestamp: new Date(),
              payload: output,
              message: `${nodeName} completed`,
            })
          }
          break
        }

        case 'token': {
          const content = data.content as string
          if (content) {
            appendToMessage(messageId, content)
          }
          break
        }

        case 'thought': {
          const thought = data.content as string
          if (thought) {
            addTrace({
              nodeId: 'gemini',
              event: 'custom',
              timestamp: new Date(),
              message: `Thinking: ${thought}`,
            })
          }
          break
        }

        case 'draft_update': {
          const draft = data.content as string
          if (draft) {
            setCurrentDraft(draft)
          }
          break
        }

        case 'progress': {
          const message = data.message as string
          if (message) {
            addTrace({
              nodeId: 'system',
              event: 'custom',
              timestamp: new Date(),
              message: message,
            })
          }
          break
        }

        case 'error':
          setGlobalHealth('critical')
          addTrace({
            nodeId: 'system',
            event: 'error',
            timestamp: new Date(),
            message: `Error: ${data.message}`,
            payload: data,
          })
          break

        case 'run_end':
          setRunning(false)
          setActiveNode(null)
          addTrace({
            nodeId: 'system',
            event: 'end',
            timestamp: new Date(),
            message: `Research completed: ${data.status}`,
          })
          break

        default:
          if (eventType.startsWith('custom_')) {
            addTrace({
              nodeId: 'system',
              event: 'custom',
              timestamp: new Date(),
              message: eventType.replace('custom_', ''),
              payload: data,
            })
          }
      }
    },
    [
      setActiveNode,
      updateNode,
      addTrace,
      addScore,
      setBoosted,
      setCurrentDraft,
      setDiagram,
      setGlobalHealth,
      setIteration,
      setRunning,
      appendToMessage,
    ]
  )

  const stopStream = useCallback(() => {
    abortControllerRef.current?.abort()
    setRunning(false)
    setStreaming(false)
  }, [setRunning, setStreaming])

  return { startStream, stopStream }
}
