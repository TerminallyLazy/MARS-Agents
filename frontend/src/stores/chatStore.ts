import { create } from 'zustand'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    iteration?: number
    score?: number
    previousScore?: number
    nodeId?: string
    isStreaming?: boolean
  }
}

interface ChatStore {
  messages: ChatMessage[]
  isStreaming: boolean
  streamingMessageId: string | null
  
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => string
  updateMessage: (id: string, content: string) => void
  appendToMessage: (id: string, content: string) => void
  setMessageMetadata: (id: string, metadata: ChatMessage['metadata']) => void
  
  setStreaming: (isStreaming: boolean, messageId?: string) => void
  
  clearMessages: () => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isStreaming: false,
  streamingMessageId: null,
  
  addMessage: (message) => {
    const id = Math.random().toString(36).substring(2, 9)
    const newMessage: ChatMessage = {
      ...message,
      id,
      timestamp: new Date(),
    }
    set((state) => ({
      messages: [...state.messages, newMessage],
    }))
    return id
  },
  
  updateMessage: (id, content) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content } : msg
      ),
    }))
  },
  
  appendToMessage: (id, content) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content: msg.content + content } : msg
      ),
    }))
  },
  
  setMessageMetadata: (id, metadata) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, metadata: { ...msg.metadata, ...metadata } } : msg
      ),
    }))
  },
  
  setStreaming: (isStreaming, messageId) => {
    set({ isStreaming, streamingMessageId: messageId ?? null })
  },
  
  clearMessages: () => set({ messages: [], isStreaming: false, streamingMessageId: null }),
}))
