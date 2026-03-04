import React from 'react'
import useChatStore from '../stores/chatStore'

function ToolsPanel() {
  const { toggleToolsPanel } = useChatStore()

  // Mock tools data - in a real implementation this would come from the store
  const tools = [
    {
      id: 1,
      name: 'intent_classifier',
      description: 'Classifies user intent and routes to appropriate workflow',
      status: 'completed',
      output: 'Routed to: data_analysis workflow'
    },
    {
      id: 2,
      name: 'workflow_planner',
      description: 'Creates execution plan with reasoning steps',
      status: 'completed',
      output: 'Generated 3-step plan'
    },
    {
      id: 3,
      name: 'data_query',
      description: 'Query and analyze data from databases',
      status: 'executing',
      output: null
    },
    {
      id: 4,
      name: 'chart_generator',
      description: 'Generate charts and visualizations',
      status: 'pending',
      output: null
    }
  ]

  return (
    <aside className="tools-panel">
      {/* Header */}
      <div className="tools-header">
        <h2 className="tools-title">
          <span className="tools-icon">🔧</span>
          Tools & Execution
        </h2>
        <button
          className="icon-button"
          onClick={toggleToolsPanel}
          title="Close panel"
        >
          ✕
        </button>
      </div>

      {/* Tools Content */}
      <div className="tools-content">
        {/* Status Overview */}
        <div style={{
          padding: '12px',
          backgroundColor: 'var(--color-bg-tertiary)',
          borderRadius: '8px',
          marginBottom: '16px'
        }}>
          <div style={{
            fontSize: '12px',
            color: 'var(--color-text-muted)',
            marginBottom: '4px'
          }}>
            Execution Status
          </div>
          <div style={{
            display: 'flex',
            gap: '12px',
            fontSize: '12px'
          }}>
            <span style={{ color: 'var(--color-success)' }}>
              ✓ 2 Completed
            </span>
            <span style={{ color: 'var(--color-warning)' }}>
              ⏳ 1 Running
            </span>
            <span style={{ color: 'var(--color-text-muted)' }}>
              ○ 1 Pending
            </span>
          </div>
        </div>

        {/* Tool Items */}
        {tools.map((tool) => (
          <div key={tool.id} className={`tool-item ${tool.status}`}>
            <div className="tool-header">
              <span className="tool-name">{tool.name}</span>
              <span className={`tool-status ${tool.status}`}>
                {tool.status === 'completed' && '✓ Done'}
                {tool.status === 'executing' && '⏳ Running'}
                {tool.status === 'pending' && '○ Pending'}
                {tool.status === 'failed' && '✕ Failed'}
              </span>
            </div>
            <div className="tool-description">{tool.description}</div>
            {tool.output && (
              <div className="tool-output">{tool.output}</div>
            )}
          </div>
        ))}

        {/* Available Skills Section */}
        <div style={{ marginTop: '24px' }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: 'var(--color-text-muted)',
            textTransform: 'uppercase',
            marginBottom: '12px'
          }}>
            Available Skills
          </div>

          <div className="tool-item" style={{ borderLeftColor: 'var(--color-primary)' }}>
            <div className="tool-header">
              <span className="tool-name">data_query</span>
              <span className="tool-status pending">Available</span>
            </div>
            <div className="tool-description">
              Query and analyze data from databases or files
            </div>
          </div>

          <div className="tool-item" style={{ borderLeftColor: 'var(--color-primary)' }}>
            <div className="tool-header">
              <span className="tool-name">chart_generator</span>
              <span className="tool-status pending">Available</span>
            </div>
            <div className="tool-description">
              Generate charts and visualizations from data
            </div>
          </div>

          <div className="tool-item" style={{ borderLeftColor: 'var(--color-primary)' }}>
            <div className="tool-header">
              <span className="tool-name">code_writer</span>
              <span className="tool-status pending">Available</span>
            </div>
            <div className="tool-description">
              Write code in various programming languages
            </div>
          </div>

          <div className="tool-item" style={{ borderLeftColor: 'var(--color-primary)' }}>
            <div className="tool-header">
              <span className="tool-name">web_search</span>
              <span className="tool-status pending">Available</span>
            </div>
            <div className="tool-description">
              Search the web for information
            </div>
          </div>

          <div className="tool-item" style={{ borderLeftColor: 'var(--color-primary)' }}>
            <div className="tool-header">
              <span className="tool-name">content_summarizer</span>
              <span className="tool-status pending">Available</span>
            </div>
            <div className="tool-description">
              Summarize long content into concise summaries
            </div>
          </div>

          <div className="tool-item" style={{ borderLeftColor: 'var(--color-primary)' }}>
            <div className="tool-header">
              <span className="tool-name">code_reviewer</span>
              <span className="tool-status pending">Available</span>
            </div>
            <div className="tool-description">
              Review code for bugs, style issues, and improvements
            </div>
          </div>
        </div>

        {/* Debug Info */}
        <div style={{
          marginTop: '24px',
          padding: '12px',
          backgroundColor: 'var(--color-bg-dark)',
          borderRadius: '8px',
          fontSize: '10px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--color-text-dark)'
        }}>
          <div style={{ color: 'var(--color-accent)', marginBottom: '4px' }}>
            Debug Console
          </div>
          <div style={{ opacity: 0.7 }}>
            [INFO] WebSocket connected<br />
            [INFO] Session initialized<br />
            [INFO] Skills loaded: 6<br />
            [INFO] Workflows registered: 4<br />
          </div>
        </div>
      </div>
    </aside>
  )
}

export default ToolsPanel
