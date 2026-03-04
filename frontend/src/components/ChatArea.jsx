import React, { useState, useRef, useEffect } from 'react'
import useChatStore from '../stores/chatStore'

const WORKFLOW_LABELS = {
  data_analysis: 'Data Analysis',
  code_gen: 'Code Generation',
  research: 'Research',
  general_chat: 'General Chat'
}

const WORKFLOW_ICONS = {
  data_analysis: '📊',
  code_gen: '💻',
  research: '🔍',
  general_chat: '💬'
}

function ChatArea() {
  const {
    messages,
    isLoading,
    currentThinking,
    selectedWorkflow,
    showToolsPanel,
    toggleToolsPanel,
    sendMessage
  } = useChatStore()

  const [inputValue, setInputValue] = useState('')
  const [openReasoning, setOpenReasoning] = useState({})
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentThinking])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`
    }
  }, [inputValue])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputValue.trim() && !isLoading) {
      sendMessage(inputValue.trim())
      setInputValue('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const toggleReasoning = (messageId) => {
    setOpenReasoning(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }))
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="chat-area">
      {/* Header */}
      <header className="chat-header">
        <div>
          <h1 className="chat-title">AI Assistant</h1>
          <p className="chat-subtitle">
            {selectedWorkflow
              ? `Mode: ${WORKFLOW_LABELS[selectedWorkflow] || selectedWorkflow}`
              : 'Auto-detecting workflow based on your input'}
          </p>
        </div>
        <div className="chat-actions">
          <button
            className="icon-button"
            onClick={toggleToolsPanel}
            title={showToolsPanel ? 'Hide Tools Panel' : 'Show Tools Panel'}
          >
            {showToolsPanel ? '📋' : '📋'}
          </button>
        </div>
      </header>

      {/* Messages Container */}
      <div className="messages-container">
        {/* Empty State */}
        {messages.length === 0 && !isLoading && (
          <div className="empty-state">
            <svg className="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <h2 className="empty-state-title">Start a Conversation</h2>
            <p className="empty-state-description">
              Ask me anything! I can help with data analysis, code generation,
              research, or just have a chat. Your request will be automatically
              routed to the best workflow.
            </p>
            <div style={{ marginTop: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <span className="workflow-badge">
                <span className="workflow-badge-icon">📊</span>
                Data Analysis
              </span>
              <span className="workflow-badge">
                <span className="workflow-badge-icon">💻</span>
                Code Gen
              </span>
              <span className="workflow-badge">
                <span className="workflow-badge-icon">🔍</span>
                Research
              </span>
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((message) => (
          <div key={message.id} className={`message-wrapper ${message.role}`}>
            <div className="message-bubble">
              <div className="message-content">{message.content}</div>
              <div className="message-timestamp">{formatTime(message.timestamp)}</div>

              {/* Reasoning Accordion for assistant messages */}
              {message.role === 'assistant' && message.reasoning_steps && message.reasoning_steps.length > 0 && (
                <div className={`reasoning-accordion ${openReasoning[message.id] ? 'open' : ''}`}>
                  <div
                    className="reasoning-header"
                    onClick={() => toggleReasoning(message.id)}
                  >
                    <span className="reasoning-title">
                      <span>🧠</span>
                      Reasoning Process
                    </span>
                    <span className="reasoning-chevron">▼</span>
                  </div>
                  <div className="reasoning-content">
                    {message.reasoning_steps.map((step, index) => (
                      <div key={index} className="reasoning-step-item">
                        <span className={`reasoning-step-badge ${step.status}`}>
                          {step.status === 'completed' ? '✓' : step.step_number}
                        </span>
                        <div>
                          <div className="reasoning-step-text">{step.description}</div>
                          {step.tool_used && (
                            <div className="reasoning-step-tool">🔧 {step.tool_used}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Thinking Indicator */}
        {isLoading && currentThinking && (
          <div className="thinking-indicator">
            <div className="thinking-header">
              <span className="thinking-icon">⚙️</span>
              <span>Thinking...</span>
              <div className="thinking-dots">
                <span className="thinking-dot"></span>
                <span className="thinking-dot"></span>
                <span className="thinking-dot"></span>
              </div>
            </div>
            <div className="thinking-text">{currentThinking}</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-area">
        <form className="input-container" onSubmit={handleSubmit}>
          <textarea
            ref={textareaRef}
            className="input-textarea"
            placeholder="Ask anything... (Shift+Enter for new line)"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
          />
          <div className="input-actions">
            <button
              type="button"
              className="attach-button"
              title="Attach file (coming soon)"
              disabled
            >
              📎
            </button>
            <button
              type="submit"
              className="send-button"
              disabled={!inputValue.trim() || isLoading}
            >
              {isLoading ? '⏳' : '➤'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ChatArea
