import { create } from 'zustand'

const useChatStore = create((set, get) => ({
  // Session state
  sessionId: null,
  isConnected: false,

  // Messages
  messages: [],
  isLoading: false,
  currentThinking: null,

  // Workflow
  selectedWorkflow: null,
  availableWorkflows: [],

  // UI State
  showToolsPanel: true,
  showHistory: false,
  theme: 'light',

  // WebSocket
  websocket: null,

  // Actions
  setSessionId: (sessionId) => set({ sessionId }),

  setConnected: (isConnected) => set({ isConnected }),

  setMessages: (messages) => set({ messages }),

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  setLoading: (isLoading) => set({ isLoading }),

  setCurrentThinking: (thinking) => set({ currentThinking: thinking }),

  setSelectedWorkflow: (workflow) => set({ selectedWorkflow: workflow }),

  setAvailableWorkflows: (workflows) => set({ availableWorkflows: workflows }),

  toggleToolsPanel: () => set((state) => ({ showToolsPanel: !state.showToolsPanel })),

  toggleHistory: () => set((state) => ({ showHistory: !state.showHistory })),

  toggleTheme: () => set((state) => ({
    theme: state.theme === 'light' ? 'dark' : 'light'
  })),

  // Connect WebSocket
  connectWebSocket: () => {
    const { websocket, isConnected } = get()

    if (websocket && isConnected) {
      return websocket
    }

    const ws = new WebSocket(`ws://${window.location.host}/ws/chat`)

    ws.onopen = () => {
      console.log('WebSocket connected')
      set({ isConnected: true, websocket: ws })
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      get().handleWebSocketMessage(data)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      set({ isConnected: false, websocket: null })
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    set({ websocket: ws })
    return ws
  },

  // Handle WebSocket messages
  handleWebSocketMessage: (data) => {
    const { messages, addMessage, setLoading, setCurrentThinking } = get()

    switch (data.type) {
      case 'start':
        setLoading(true)
        setCurrentThinking('Analyzing your request...')
        break

      case 'intent':
        setCurrentThinking(`Detected intent: ${data.workflow}`)
        break

      case 'plan':
        setCurrentThinking(`Planning ${data.steps.length} steps...`)
        break

      case 'step_start':
        setCurrentThinking(`Executing step ${data.step_number}: ${data.description}`)
        break

      case 'step_complete':
        if (data.success) {
          setCurrentThinking(`Step ${data.step_number} completed`)
        }
        break

      case 'complete':
        setLoading(false)
        setCurrentThinking(null)
        addMessage({
          id: Date.now(),
          role: 'assistant',
          content: data.message,
          timestamp: new Date().toISOString()
        })
        set({ sessionId: data.session_id })
        break

      case 'error':
        setLoading(false)
        setCurrentThinking(null)
        addMessage({
          id: Date.now(),
          role: 'system',
          content: `Error: ${data.message}`,
          timestamp: new Date().toISOString()
        })
        break

      default:
        break
    }
  },

  // Send message
  sendMessage: async (content) => {
    const { websocket, connectWebSocket, selectedWorkflow } = get()

    // Add user message
    get().addMessage({
      id: Date.now(),
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    })

    // Connect if not connected
    let ws = websocket
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      ws = connectWebSocket()
      // Wait for connection
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    // Send message
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        message: content,
        workflow_override: selectedWorkflow
      }))
    }
  },

  // Load workflows from API
  loadWorkflows: async () => {
    try {
      const response = await fetch('/api/workflows')
      const workflows = await response.json()
      set({ availableWorkflows: workflows })
    } catch (error) {
      console.error('Failed to load workflows:', error)
    }
  }
}))

export default useChatStore
