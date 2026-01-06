import { useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'
import type { ChatMessage } from '@/stores/chatStore'

interface ChatContainerProps {
  messages: ChatMessage[]
  isStreaming?: boolean
  className?: string
}

export function ChatContainer({
  messages,
  isStreaming = false,
  className,
}: ChatContainerProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isStreaming])

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className="px-4 py-3 border-b border-[var(--border-default)]">
        <h2 className="font-semibold text-[var(--text-loud)]">Conversation</h2>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
      >
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-12 h-12 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center mb-3">
              <span className="material-symbols-outlined text-[var(--text-muted)]">
                chat_bubble_outline
              </span>
            </div>
            <p className="text-[var(--text-muted)]">
              Start a conversation by sending a message
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}

        {isStreaming && <TypingIndicator />}
      </div>
    </div>
  )
}
