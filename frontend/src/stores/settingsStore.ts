import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'system'
type ResearchBackend = 'langgraph' | 'gemini'

interface SettingsStore {
  theme: Theme
  researchBackend: ResearchBackend
  sidebarOpen: boolean
  sidebarCollapsed: boolean
  showTracePanel: boolean
  showAgentGraph: boolean
  autoScrollTraces: boolean
  
  setTheme: (theme: Theme) => void
  setResearchBackend: (backend: ResearchBackend) => void
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleTracePanel: () => void
  toggleAgentGraph: () => void
  setAutoScrollTraces: (autoScroll: boolean) => void
  
  getResolvedTheme: () => 'light' | 'dark'
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      theme: 'system',
      researchBackend: 'gemini',
      sidebarOpen: true,
      sidebarCollapsed: false,
      showTracePanel: true,
      showAgentGraph: true,
      autoScrollTraces: true,
      
      setTheme: (theme) => {
        set({ theme })
        applyTheme(theme)
      },
      
      setResearchBackend: (backend) => set({ researchBackend: backend }),
      
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      
      toggleTracePanel: () => set((state) => ({ showTracePanel: !state.showTracePanel })),
      
      toggleAgentGraph: () => set((state) => ({ showAgentGraph: !state.showAgentGraph })),
      
      setAutoScrollTraces: (autoScroll) => set({ autoScrollTraces: autoScroll }),
      
      getResolvedTheme: () => {
        const { theme } = get()
        if (theme === 'system') {
          return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        }
        return theme
      },
    }),
    {
      name: 'mars-settings',
      partialize: (state) => ({
        theme: state.theme,
        researchBackend: state.researchBackend,
        sidebarCollapsed: state.sidebarCollapsed,
        showTracePanel: state.showTracePanel,
        showAgentGraph: state.showAgentGraph,
        autoScrollTraces: state.autoScrollTraces,
      }),
    }
  )
)

function applyTheme(theme: Theme) {
  const root = document.documentElement
  const isDark =
    theme === 'dark' ||
    (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  
  root.classList.toggle('dark', isDark)
}

if (typeof window !== 'undefined') {
  const stored = localStorage.getItem('mars-settings')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      applyTheme(parsed.state?.theme ?? 'system')
    } catch {
      applyTheme('system')
    }
  } else {
    applyTheme('system')
  }
  
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const { theme } = useSettingsStore.getState()
    if (theme === 'system') {
      applyTheme('system')
    }
  })
}
