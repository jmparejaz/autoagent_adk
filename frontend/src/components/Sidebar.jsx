import React from 'react'
import useChatStore from '../stores/chatStore'

const WORKFLOW_ICONS = {
  data_analysis: '📊',
  code_gen: '💻',
  research: '🔍',
  general_chat: '💬'
}

const WORKFLOW_LABELS = {
  data_analysis: 'Data Analysis',
  code_gen: 'Code Generation',
  research: 'Research',
  general_chat: 'General Chat'
}

function Sidebar() {
  const {
    availableWorkflows,
    selectedWorkflow,
    setSelectedWorkflow,
    theme,
    toggleTheme,
    isConnected
  } = useChatStore()

  return (
    <aside className="sidebar">
      {/* Header with Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <img src="/logo.svg" alt="Logo" />
          <div>
            <div className="sidebar-logo-text">Agent Platform</div>
            <div className="sidebar-logo-subtitle">Powered by Google ADK</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {/* Workflows Section */}
        <div className="sidebar-section">
          <div className="sidebar-section-title">Workflows</div>
          <ul className="workflow-list">
            {availableWorkflows.map((workflow) => (
              <li
                key={workflow.type}
                className={`workflow-item ${selectedWorkflow === workflow.type ? 'active' : ''}`}
                onClick={() => setSelectedWorkflow(workflow.type)}
              >
                <span className="workflow-icon">
                  {WORKFLOW_ICONS[workflow.type] || '📋'}
                </span>
                <span className="workflow-name">
                  {WORKFLOW_LABELS[workflow.type] || workflow.name}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Quick Actions */}
        <div className="sidebar-section">
          <div className="sidebar-section-title">Quick Actions</div>
          <ul className="workflow-list">
            <li
              className="workflow-item"
              onClick={() => setSelectedWorkflow(null)}
            >
              <span className="workflow-icon">🚀</span>
              <span className="workflow-name">Auto Detect</span>
            </li>
            <li
              className="workflow-item"
              onClick={() => {
                if (window.confirm('Clear chat history?')) {
                  window.location.reload()
                }
              }}
            >
              <span className="workflow-icon">🗑️</span>
              <span className="workflow-name">Clear History</span>
            </li>
          </ul>
        </div>

        {/* Settings */}
        <div className="sidebar-section">
          <div className="sidebar-section-title">Settings</div>
          <ul className="workflow-list">
            <li className="workflow-item" onClick={toggleTheme}>
              <span className="workflow-icon">
                {theme === 'light' ? '🌙' : '☀️'}
              </span>
              <span className="workflow-name">
                {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
              </span>
            </li>
          </ul>
        </div>
      </nav>

      {/* Footer with Mascot */}
      <div className="sidebar-footer">
        <div className="mascot-container">
          <img
            src="/mascot/mascot-idle.svg"
            alt="Mascot"
            className="mascot-image"
          />
          <div className="mascot-name">Marina</div>
          <div className="mascot-status">
            {isConnected ? '🟢 Online' : '🔴 Connecting...'}
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
