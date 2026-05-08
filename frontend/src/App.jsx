import { useState } from 'react'
import { predictUrl, explainUrl, analyzeUrl } from './api'
import './index.css'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('detection')

  const scanTime = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC'

  const handleScan = async (e) => {
    e.preventDefault()
    if (!url.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    setExplanation(null)
    setAnalysis(null)
    setActiveTab('detection')
    try {
      const [pred, anal] = await Promise.all([predictUrl(url), analyzeUrl(url)])
      setResult(pred)
      setAnalysis(anal)
      const expl = await explainUrl(url)
      setExplanation(expl)
    } catch (err) {
      setError(err.message || 'An error occurred during analysis.')
    } finally {
      setLoading(false)
    }
  }

  const scoreColor = (score) => {
    if (score === undefined) return '#6b7280'
    if (score >= 40) return '#ff003c'
    if (score >= 20) return '#ffb800'
    return '#00ff66'
  }

  const predColor = (p) => {
    if (p === 'Safe') return '#00ff66'
    if (p === 'Homograph') return '#ffb800'
    if (p === 'Phishing') return '#ff003c'
    return '#6b7280'
  }

  const tabs = [
    { id: 'detection', label: 'Detection' },
    { id: 'details', label: 'Details' },
    { id: 'analysis', label: 'Analysis' },
  ]

  const searchForm = (
    <form onSubmit={handleScan} className="nav-search">
      <div className="search-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      </div>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Search or scan a URL, domain, or IP address"
        className="search-input"
        disabled={loading}
      />
      <button 
        type="submit" 
        disabled={loading || !url.trim()} 
        className="search-btn"
      >
        <div className="btn-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <span>{loading ? 'Scanning...' : 'Scan'}</span>
      </button>
    </form>
  )

  return (
    <div className="app-root">
      {/* Top nav bar */}
      <nav className="top-nav">
        <div className="nav-inner">
          <div 
            className="nav-brand" 
            onClick={() => {
              setResult(null)
              setUrl('')
              setError(null)
            }}
            style={{ cursor: 'pointer' }}
            title="Return to Home"
          >
            <span className="brand-icon">◈</span>
            <span className="brand-text">PhishBERT-XAI</span>
          </div>
          {(result || loading || error) && (
            <button 
              onClick={() => {
                setResult(null)
                setUrl('')
                setError(null)
              }}
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--border)',
                color: 'var(--text-primary)',
                padding: '6px 14px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                marginLeft: '12px'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
              Home
            </button>
          )}
          {(result || loading || error) && searchForm}
        </div>
      </nav>

      {/* Landing state */}
      {!result && !loading && !error && (
        <div className="landing">
          <div className="landing-content">
            <div className="landing-icon">◈</div>
            <h1 className="landing-title">PhishBERT-XAI</h1>
            <p className="landing-sub">Deep Learning URL Threat Analysis with Character-Level Explainability</p>
            
            <div className="landing-search-container">
              {searchForm}
            </div>

            <div className="landing-features">
              <div className="feature-chip"><span className="chip-dot safe" />CANINE Transformer</div>
              <div className="feature-chip"><span className="chip-dot warn" />Homoglyph Detection</div>
              <div className="feature-chip"><span className="chip-dot danger" />Phishing Classification</div>
              <div className="feature-chip"><span className="chip-dot accent" />XAI Explainability</div>
            </div>
          </div>
        </div>
      )}

      {/* Loading spinner */}
      {loading && (
        <div className="landing">
          <div className="spinner" />
          <p className="landing-sub" style={{marginTop: 16}}>Analyzing URL with CANINE transformer...</p>
        </div>
      )}

      {error && (
        <div className="error-banner">ERROR: {error}</div>
      )}

      {/* Results */}
      {result && analysis && (
        <div className="results-container">
          {/* Header card — VirusTotal style */}
          <div className="result-header">
            <div className="header-left">
              {/* Score ring */}
              <div className="score-ring-container">
                <svg viewBox="0 0 120 120" className="score-ring">
                  <circle cx="60" cy="60" r="52" fill="none" stroke="#1a1a2e" strokeWidth="8" />
                  <circle
                    cx="60" cy="60" r="52"
                    fill="none"
                    stroke={scoreColor(analysis.summary.threat_score)}
                    strokeWidth="8"
                    strokeDasharray={`${(analysis.summary.failed / analysis.summary.total_checks) * 327} 327`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                    style={{ transition: 'stroke-dasharray 1s ease' }}
                  />
                </svg>
                <div className="score-text">
                  <span className="score-num" style={{ color: scoreColor(analysis.summary.threat_score) }}>
                    {analysis.summary.failed}
                  </span>
                  <span className="score-denom">/ {analysis.summary.total_checks}</span>
                </div>
                <div className="score-label">Security Checks</div>
              </div>
            </div>

            <div className="header-right">
              {/* Status banner */}
              <div className="status-banner" style={{ borderColor: predColor(result.prediction) + '40', background: predColor(result.prediction) + '10' }}>
                <span className="status-dot" style={{ background: predColor(result.prediction) }} />
                <span style={{ color: predColor(result.prediction) }}>
                  {result.prediction === 'Safe' && 'URL classified as Safe — No threats detected'}
                  {result.prediction === 'Homograph' && 'Warning: Homoglyph attack detected — Visually deceptive domain'}
                  {result.prediction === 'Phishing' && 'Danger: URL classified as Phishing — Potential credential theft'}
                </span>
                <span className="confidence-badge" style={{ color: predColor(result.prediction), borderColor: predColor(result.prediction) + '40' }}>
                  {(result.confidence * 100).toFixed(1)}% confidence
                </span>
              </div>

              {/* URL info row */}
              <div className="url-info-row">
                <div className="url-display">
                  <div className="url-text">{url}</div>
                  <div className="url-cleaned">{result.cleaned_url}</div>
                </div>
                <div className="url-meta">
                  <div className="meta-item">
                    <span className="meta-label">Classification</span>
                    <span className="meta-value" style={{ color: predColor(result.prediction) }}>{result.prediction}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Risk Level</span>
                    <span className="meta-value" style={{ color: scoreColor(analysis.summary.threat_score) }}>{analysis.summary.risk_level}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Analysis Date</span>
                    <span className="meta-value">{scanTime.split(' ')[0]}</span>
                  </div>
                </div>
              </div>

              {/* Tags */}
              <div className="tag-row">
                <span className="tag tag-model">canine-c</span>
                <span className="tag tag-type">character-level</span>
                <span className="tag tag-type">3-class</span>
                {analysis.summary.risk_level === 'High' && <span className="tag tag-danger">high-risk</span>}
                {analysis.checks.find(c => c.name === 'URL Shortener' && c.status !== 'pass') && <span className="tag tag-warn">url-shortener</span>}
                {analysis.checks.find(c => c.name === 'Unicode / IDN' && c.status !== 'pass') && <span className="tag tag-warn">unicode-idn</span>}
                {analysis.checks.find(c => c.name === 'Brand Impersonation' && c.status === 'fail') && <span className="tag tag-danger">brand-spoof</span>}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="tabs-bar">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'tab-active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label.toUpperCase()}
                {tab.id === 'detection' && <span className="tab-badge">{analysis.summary.total_checks}</span>}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="tab-content">
            {activeTab === 'detection' && (
              <div className="detection-tab">
                {/* Vendor-style results */}
                <div className="section-block">
                  <h3 className="section-title">Security Checks <span className="section-info">ⓘ</span></h3>
                  <div className="vendor-list">
                    {analysis.checks.map((check, idx) => (
                      <div key={idx} className="vendor-row">
                        <span className="vendor-name">{check.name}</span>
                        <span className={`vendor-result ${check.status}`}>{check.detail}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="section-block">
                  <h3 className="section-title">History <span className="section-info">⏱</span></h3>
                  <div className="history-list">
                    <div className="history-row"><span className="history-label">Scan Performed</span><span className="history-value">{scanTime}</span></div>
                    <div className="history-row"><span className="history-label">Model</span><span className="history-value">CANINE-c (google/canine-c)</span></div>
                    <div className="history-row"><span className="history-label">Dataset</span><span className="history-value">Mitake/PhishingURLsANDBenignURLs</span></div>
                    <div className="history-row"><span className="history-label">Explainability</span><span className="history-value">Leave-One-Out Perturbation</span></div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'details' && (
              <div className="details-tab">
                <div className="section-block">
                  <h3 className="section-title">Character-Level Importance <span className="section-info">ⓘ</span></h3>
                  <p className="section-desc">Each character is evaluated by masking it and measuring the confidence drop. Highlighted characters contribute most to the <strong style={{color: predColor(result.prediction)}}>{result.prediction}</strong> classification.</p>
                  {explanation ? (
                    <div className="char-display">
                      {explanation.shap_values.map((item, idx) => {
                        const isPositive = item.importance > 0
                        const absImp = Math.abs(item.importance)
                        const maxImp = Math.max(...explanation.shap_values.map(i => Math.abs(i.importance)))
                        const opacity = maxImp > 0.001 ? Math.min(1.0, (absImp / maxImp)) : 0
                        const bgColor = isPositive && opacity > 0.1
                          ? (result.prediction === 'Phishing' ? `rgba(255,0,60,${opacity})` : result.prediction === 'Homograph' ? `rgba(255,184,0,${opacity})` : `rgba(0,255,102,${opacity})`)
                          : 'transparent'
                        return (
                          <span key={idx} className="char-cell" style={{ backgroundColor: bgColor, color: isPositive && opacity > 0.3 ? '#fff' : '#9ca3af' }} title={`'${item.char}' → importance: ${item.importance.toFixed(4)}`}>
                            {item.char}
                          </span>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="loading-placeholder"><div className="spinner-sm" /><span>Analyzing characters...</span></div>
                  )}
                </div>

                <div className="section-block">
                  <h3 className="section-title">URL Components <span className="section-info">⏱</span></h3>
                  <div className="history-list">
                    <div className="history-row"><span className="history-label">Scheme</span><span className="history-value">{analysis.components.scheme}</span></div>
                    <div className="history-row"><span className="history-label">Domain</span><span className="history-value">{analysis.components.domain || '—'}</span></div>
                    <div className="history-row"><span className="history-label">TLD</span><span className="history-value">{analysis.components.tld || '—'}</span></div>
                    <div className="history-row"><span className="history-label">Subdomains</span><span className="history-value">{analysis.components.subdomain_count}</span></div>
                    <div className="history-row"><span className="history-label">Path</span><span className="history-value">{analysis.components.path || 'none'}</span></div>
                    <div className="history-row"><span className="history-label">Query Parameters</span><span className="history-value">{analysis.components.query_params}</span></div>
                    <div className="history-row"><span className="history-label">Port</span><span className="history-value">{String(analysis.components.port || 'default')}</span></div>
                    <div className="history-row"><span className="history-label">Total Length</span><span className="history-value">{analysis.components.full_length} characters</span></div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'analysis' && (
              <div className="analysis-tab">
                <div className="section-block">
                  <h3 className="section-title">Threat Summary <span className="section-info">ⓘ</span></h3>
                  <div className="summary-grid">
                    <div className="summary-card safe"><div className="summary-num">{analysis.summary.passed}</div><div className="summary-label">Passed</div></div>
                    <div className="summary-card warn"><div className="summary-num">{analysis.summary.warnings}</div><div className="summary-label">Warnings</div></div>
                    <div className="summary-card danger"><div className="summary-num">{analysis.summary.failed}</div><div className="summary-label">Failed</div></div>
                    <div className="summary-card accent"><div className="summary-num">{analysis.summary.threat_score}</div><div className="summary-label">Threat Score</div></div>
                  </div>
                </div>

                <div className="section-block">
                  <h3 className="section-title">Model Output <span className="section-info">ⓘ</span></h3>
                  <div className="history-list">
                    <div className="history-row"><span className="history-label">Input URL</span><span className="history-value">{url}</span></div>
                    <div className="history-row"><span className="history-label">Preprocessed</span><span className="history-value">{result.cleaned_url}</span></div>
                    <div className="history-row"><span className="history-label">Prediction</span><span className="history-value" style={{color: predColor(result.prediction)}}>{result.prediction}</span></div>
                    <div className="history-row"><span className="history-label">Confidence</span><span className="history-value">{(result.confidence * 100).toFixed(2)}%</span></div>
                    <div className="history-row"><span className="history-label">Model Architecture</span><span className="history-value">CANINE-c (12 layers, 768 hidden, character-level)</span></div>
                    <div className="history-row"><span className="history-label">Max Sequence Length</span><span className="history-value">128 characters</span></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
