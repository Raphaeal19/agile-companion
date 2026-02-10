import { useState } from 'react'
import { FileText, Zap, AlertTriangle, Megaphone, Loader2, Shield, Key, Info } from 'lucide-react'
import './App.css'

function App() {
  const [transcript, setTranscript] = useState('')
  const [modelChoice, setModelChoice] = useState('gemini-2.0-flash')
  const [documentation, setDocumentation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('backlog')
  const [showApiInfo, setShowApiInfo] = useState(false)
  const getSeverityColor = (severity) => {
    const colors = {
      'Low': 'var(--success)',
      'Medium': 'var(--warning)',
      'High': 'var(--danger)',
      'Critical': '#9333ea'  // Purple for critical
    }
    return colors[severity] || 'var(--secondary)'
  }

  const exampleTranscript = `Product Manager: We need to add a user authentication system.
Developer: Should we support OAuth providers like Google and GitHub?
PM: Yes, and we also need email/password login with password reset.
Designer: The login page should have our new brand colors.
PM: Agreed. Also, we're killing the old export feature - nobody uses it.
Tech Lead: We'll need to handle rate limiting for login attempts.
PM: Good point. Let's also add two-factor authentication, but that can be a separate story.`

  const generateDocs = async () => {
    if (!transcript.trim()) {
      setError('Please enter a transcript')
      return
    }

    setLoading(true)
    setError(null)
    setDocumentation(null)

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript,
          model_choice: modelChoice
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate documentation')
      }

      const data = await response.json()
      setDocumentation(data)
      setActiveTab('backlog')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadExample = () => {
    setTranscript(exampleTranscript)
  }

  const getComplexityColor = (complexity) => {
    const colors = {
      'XS': 'var(--success)',
      'S': 'var(--success)',
      'M': 'var(--warning)',
      'L': 'var(--danger)',
      'XL': 'var(--danger)',
      'Needs Discussion': 'var(--info)'
    }
    return colors[complexity] || 'var(--secondary)'
  }

  const getPriorityColor = (priority) => {
    const colors = {
      'Must Have': 'var(--danger)',
      'Should Have': 'var(--warning)',
      'Could Have': 'var(--info)',
      'Won\'t Have': 'var(--secondary)'
    }
    return colors[priority] || 'var(--secondary)'
  }

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <h1>🤖 AI Agile Companion</h1>
          <p>Transform meeting transcripts into structured Agile documentation</p>

          {/* Demo Mode Banner */}
          <div className="demo-banner">
            <Info size={16} />
            <span>
              <strong>Demo Mode:</strong> Try it for free! Limited to 5 generations per hour.
              <button
                onClick={() => setShowApiInfo(!showApiInfo)}
                className="link-button"
              >
                Want unlimited access?
              </button>
            </span>
          </div>

          {/* API Key Instructions (Collapsible) */}
          {showApiInfo && (
            <div className="api-info-box">
              <h3>
                <Key size={20} />
                Get Your Own API Key (Free!)
              </h3>
              <ol>
                <li>
                  Go to{' '}
                  <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">
                    Google AI Studio
                  </a>
                </li>
                <li>Click "Create API Key"</li>
                <li>Copy your key</li>
                <li>
                  Run this app locally with your key:
                  <pre>
                    git clone https://github.com/YOUR_USERNAME/ai-agile-companion
                    cd ai-agile-companion/backend
                    echo "GEMINI_API_KEY=your_key_here" &gt; .env
                    python -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                    uvicorn main:app --reload
                  </pre>
                </li>
              </ol>
              <p className="note">
                📝 <strong>Note:</strong> Google's free tier includes 60 requests per minute!
              </p>
            </div>
          )}
        </div>
      </header>

      <main className="container">
        {/* Input Section */}
        <section className="input-section">
          <div className="controls">
            <select
              value={modelChoice}
              onChange={(e) => setModelChoice(e.target.value)}
              className="model-select"
            >
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (Fast)</option>
              <option value="gemini-2.5-pro">Gemini 2.5 Pro (Accurate)</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash (Legacy)</option>
            </select>
            <button onClick={loadExample} className="btn-secondary">
              Load Example
            </button>
          </div>

          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste your meeting transcript here...&#10;&#10;Example:&#10;PM: We need a login feature...&#10;Dev: Should we support OAuth?&#10;PM: Yes, Google and GitHub..."
            rows={12}
            className="transcript-input"
          />

          <button
            onClick={generateDocs}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? (
              <>
                <Loader2 className="spin" size={20} />
                Generating Documentation...
              </>
            ) : (
              'Generate Documentation Package'
            )}
          </button>
        </section>

        {/* Error Display */}
        {error && (
          <div className={error.includes('Rate limit') ? 'error-banner rate-limit' : 'error-banner'}>
            ⚠️ {error}
            {error.includes('Rate limit') && (
              <button
                onClick={() => setShowApiInfo(true)}
                className="error-action-button"
              >
                Get Unlimited Access
              </button>
            )}
          </div>
        )}

        {/* Results Section */}
        {documentation && (
          <section className="results">
            <div className="summary-card">
              <h3>Meeting Summary</h3>
              <p>{documentation.meeting_summary}</p>
            </div>

            {/* Tabs */}
            <div className="tabs">
              <button
                className={activeTab === 'backlog' ? 'tab active' : 'tab'}
                onClick={() => setActiveTab('backlog')}
              >
                <FileText size={18} />
                Product Backlog ({documentation.backlog_items.length})
              </button>
              <button
                className={activeTab === 'scope' ? 'tab active' : 'tab'}
                onClick={() => setActiveTab('scope')}
              >
                <Shield size={18} />
                Scope Sentinel
                {documentation.scope_sentinel.overall_risk !== 'Low' && (
                  <span className="tab-badge" style={{
                    backgroundColor: getSeverityColor(documentation.scope_sentinel.overall_risk)
                  }}>
                    {documentation.scope_sentinel.alerts.length}
                  </span>
                )}
              </button>
              <button
                className={activeTab === 'decisions' ? 'tab active' : 'tab'}
                onClick={() => setActiveTab('decisions')}
              >
                <Zap size={18} />
                Decisions & Risks
              </button>
              <button
                className={activeTab === 'release' ? 'tab active' : 'tab'}
                onClick={() => setActiveTab('release')}
              >
                <Megaphone size={18} />
                Release Notes
              </button>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
              {activeTab === 'backlog' && (
                <div className="backlog-view">
                  <div className="stats">
                    <span>
                      ✅ Ready: {documentation.backlog_items.filter(i => i.definition_of_ready_status === 'Ready for Sprint').length}
                    </span>
                    <span>
                      ⚠️ Needs Refinement: {documentation.backlog_items.filter(i => i.definition_of_ready_status === 'Needs Refinement').length}
                    </span>
                  </div>

                  {documentation.backlog_items.map((item, index) => (
                    <div key={index} className="backlog-item">
                      <div className="item-header">
                        <span className="item-id">{item.id}</span>
                        <h4>{item.title}</h4>
                        <div className="item-badges">
                          <span
                            className="badge"
                            style={{ backgroundColor: getPriorityColor(item.priority) }}
                          >
                            {item.priority}
                          </span>
                          <span
                            className="badge"
                            style={{ backgroundColor: getComplexityColor(item.complexity) }}
                          >
                            Size: {item.complexity}
                          </span>
                          <span className={`badge ${item.definition_of_ready_status === 'Ready for Sprint' ? 'badge-success' : 'badge-warning'}`}>
                            {item.definition_of_ready_status === 'Ready for Sprint' ? '✅ Ready' : '⚠️ Needs Work'}
                          </span>
                        </div>
                      </div>

                      <div className="user-story">
                        <p>{item.user_story}</p>
                      </div>

                      {item.missing_info && item.missing_info.trim() && (
                        <div className="missing-info">
                          <AlertTriangle size={16} />
                          <strong>Missing Information:</strong> {item.missing_info}
                        </div>
                      )}

                      <div className="acceptance-criteria">
                        <h5>Acceptance Criteria:</h5>
                        <ul>
                          {item.acceptance_criteria.map((ac, i) => (
                            <li key={i}>
                              <span className="test-type">{ac.test_type}</span>
                              {ac.condition}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'scope' && (
                <div className="scope-view">
                  <div className="scope-header">
                    <div className="overall-risk" style={{
                      borderColor: getSeverityColor(documentation.scope_sentinel.overall_risk)
                    }}>
                      <h3>Overall Risk Level</h3>
                      <div className="risk-badge" style={{
                        backgroundColor: getSeverityColor(documentation.scope_sentinel.overall_risk)
                      }}>
                        {documentation.scope_sentinel.overall_risk}
                      </div>
                      <p>{documentation.scope_sentinel.summary}</p>
                    </div>

                    <div className="scope-metrics">
                      <h4>Meeting Metrics</h4>
                      <div className="metrics-grid">
                        <div className="metric">
                          <span className="metric-value">
                            {documentation.scope_sentinel.metrics.features_discussed}
                          </span>
                          <span className="metric-label">Features Discussed</span>
                        </div>
                        <div className="metric">
                          <span className="metric-value">
                            {documentation.scope_sentinel.metrics.new_items_added}
                          </span>
                          <span className="metric-label">New Items Added</span>
                        </div>
                        <div className="metric">
                          <span className="metric-value">
                            {documentation.scope_sentinel.metrics.complexity_increases}
                          </span>
                          <span className="metric-label">Complexity Increases</span>
                        </div>
                        <div className="metric">
                          <span className="metric-value">
                            {documentation.scope_sentinel.metrics.unclear_requirements}
                          </span>
                          <span className="metric-label">Unclear Requirements</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <h3>Scope Alerts</h3>
                  {documentation.scope_sentinel.alerts.length === 0 ? (
                    <div className="empty-state success">
                      ✅ No scope creep detected! The meeting stayed focused.
                    </div>
                  ) : (
                    documentation.scope_sentinel.alerts.map((alert, i) => (
                      <div key={i} className="scope-alert" style={{
                        borderLeftColor: getSeverityColor(alert.severity)
                      }}>
                        <div className="alert-header">
                          <span className="alert-category">{alert.category}</span>
                          <span
                            className="severity-badge"
                            style={{ backgroundColor: getSeverityColor(alert.severity) }}
                          >
                            {alert.severity}
                          </span>
                        </div>

                        <p className="alert-description"><strong>{alert.description}</strong></p>

                        <div className="alert-quote">
                          <AlertTriangle size={16} />
                          <em>"{alert.quote}"</em>
                        </div>

                        <div className="alert-recommendation">
                          <strong>Recommendation:</strong> {alert.recommendation}
                        </div>

                        {alert.impacted_items.length > 0 && (
                          <div className="impacted-items">
                            <strong>Impacted Items:</strong> {alert.impacted_items.join(', ')}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'decisions' && (
                <div className="decisions-view">
                  <div className="two-column">
                    <div>
                      <h3>📝 Decision Log</h3>
                      {documentation.decision_log.length === 0 ? (
                        <p className="empty-state">No decisions recorded</p>
                      ) : (
                        documentation.decision_log.map((decision, i) => (
                          <div key={i} className="decision-card">
                            <h4>{decision.topic}</h4>
                            <p><strong>Decision:</strong> {decision.decision_made}</p>
                            <p><strong>Rationale:</strong> {decision.rationale}</p>
                            <p className="owner">Owner: {decision.owner}</p>
                          </div>
                        ))
                      )}
                    </div>

                    <div>
                      <h3>🛡️ Risk Register</h3>
                      {documentation.risk_register.length === 0 ? (
                        <p className="empty-state">No risks identified</p>
                      ) : (
                        documentation.risk_register.map((risk, i) => (
                          <div key={i} className="risk-card">
                            <div className="risk-header">
                              <span className="risk-category">{risk.category}</span>
                              <span className={`impact impact-${risk.impact.toLowerCase()}`}>
                                {risk.impact} Impact
                              </span>
                            </div>
                            <p><strong>{risk.description}</strong></p>
                            <p className="mitigation">
                              <strong>Mitigation:</strong> {risk.mitigation_strategy}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'release' && (
                <div className="release-view">
                  <h3>📢 Draft Release Notes</h3>
                  {documentation.release_notes_draft.length === 0 ? (
                    <p className="empty-state">No release notes generated</p>
                  ) : (
                    documentation.release_notes_draft.map((note, i) => (
                      <div key={i} className="release-note">
                        <h4>{note.feature_name}</h4>
                        <span className="audience-badge">{note.audience}</span>
                        <p>{note.value_statement}</p>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Powered by Google Gemini AI • Built for Agile Teams</p>
      </footer>
    </div>
  )
}

export default App