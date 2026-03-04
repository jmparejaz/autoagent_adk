import React, { useEffect } from 'react'
import useChatStore from './stores/chatStore'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import ToolsPanel from './components/ToolsPanel'
import './styles/global.css'
import './styles/app.css'

function App() {
  const { theme, showToolsPanel, loadWorkflows, connectWebSocket } = useChatStore()

  useEffect(() => {
    // Apply theme
    document.documentElement.setAttribute('data-theme', theme)

    // Load workflows
    loadWorkflows()

    // Connect WebSocket
    connectWebSocket()
  }, [])

  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <ChatArea />
      </main>
      {showToolsPanel && <ToolsPanel />}
    </div>
  )
}

export default App
