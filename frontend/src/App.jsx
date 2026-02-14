import React, { useState, useEffect, useRef, useCallback } from 'react'

// ─── API Helpers ───
const API = 'http://localhost:8080'

async function fetchJSON(path) {
    const res = await fetch(`${API}${path}`)
    return res.json()
}

async function postJSON(path, body) {
    const res = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })
    return res.json()
}

// ─── Sidebar ───
function Sidebar({ activeView, setActiveView, connected }) {
    const navItems = [
        { id: 'chat', icon: '💬', label: 'Chat' },
        { id: 'knowledge', icon: '🧠', label: 'Knowledge Base' },
        { id: 'status', icon: '📊', label: 'System Status' },
    ]

    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <div className="sidebar-brand-icon">🤖</div>
                <div>
                    <h1>JARVIS AI</h1>
                    <span>v2.0 — Advanced Architecture</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map(item => (
                    <div
                        key={item.id}
                        className={`nav-item ${activeView === item.id ? 'active' : ''}`}
                        onClick={() => setActiveView(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <span className={`status-dot ${connected ? '' : 'disconnected'}`} />
                <span>{connected ? 'Backend connected' : 'Disconnected'}</span>
            </div>
        </aside>
    )
}

// ─── Chat Panel ───
function ChatPanel() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)
    const wsRef = useRef(null)
    const [streaming, setStreaming] = useState(false)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    // WebSocket connection for streaming
    useEffect(() => {
        const connectWS = () => {
            try {
                const ws = new WebSocket('ws://localhost:8080/ws/chat')
                wsRef.current = ws

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data)

                    if (data.type === 'thinking') {
                        setLoading(true)
                    } else if (data.type === 'token') {
                        setStreaming(true)
                        setLoading(false)
                        setMessages(prev => {
                            const last = prev[prev.length - 1]
                            if (last && last.role === 'assistant' && last.streaming) {
                                return [
                                    ...prev.slice(0, -1),
                                    { ...last, content: last.content + data.text }
                                ]
                            }
                            return [...prev, { role: 'assistant', content: data.text, streaming: true, time: new Date() }]
                        })
                    } else if (data.type === 'complete') {
                        setStreaming(false)
                        setLoading(false)
                        setMessages(prev => {
                            const last = prev[prev.length - 1]
                            if (last && last.role === 'assistant' && last.streaming) {
                                return [
                                    ...prev.slice(0, -1),
                                    { ...last, content: data.text, streaming: false }
                                ]
                            }
                            return [...prev, { role: 'assistant', content: data.text, time: new Date() }]
                        })
                    }
                }

                ws.onclose = () => {
                    setTimeout(connectWS, 3000)
                }
            } catch (e) {
                console.log('WebSocket connection failed, will retry')
            }
        }

        connectWS()
        return () => wsRef.current?.close()
    }, [])

    const sendMessage = useCallback(async () => {
        if (!input.trim() || loading || streaming) return
        const userMsg = input.trim()
        setInput('')

        setMessages(prev => [...prev, { role: 'user', content: userMsg, time: new Date() }])

        // Try WebSocket first
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            setLoading(true)
            wsRef.current.send(JSON.stringify({ message: userMsg }))
        } else {
            // Fallback to REST
            setLoading(true)
            try {
                const data = await postJSON('/api/chat', { message: userMsg })
                setMessages(prev => [...prev, { role: 'assistant', content: data.response, time: new Date() }])
            } catch (e) {
                setMessages(prev => [...prev, { role: 'assistant', content: `Connection error: ${e.message}`, time: new Date() }])
            }
            setLoading(false)
        }
    }, [input, loading, streaming])

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    const formatTime = (date) => {
        if (!date) return ''
        const d = new Date(date)
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    if (messages.length === 0 && !loading) {
        return (
            <div className="chat-container">
                <div className="chat-messages">
                    <div className="empty-state">
                        <div className="empty-state-icon">🤖</div>
                        <h3>Hello, I'm Jarvis</h3>
                        <p>Your AI assistant with vector memory and RAG-powered responses. Ask me anything!</p>
                    </div>
                </div>
                <div className="chat-input-area">
                    <div className="chat-input-wrapper">
                        <input
                            className="chat-input"
                            placeholder="Type a message..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            id="chat-input"
                        />
                        <button className="chat-send-btn" onClick={sendMessage} disabled={!input.trim()} id="chat-send">
                            ➤
                        </button>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="chat-container">
            <div className="chat-messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`message ${msg.role}`}>
                        <div className="message-avatar">
                            {msg.role === 'assistant' ? '🤖' : '👤'}
                        </div>
                        <div>
                            <div className="message-content">{msg.content}</div>
                            <div className="message-time">{formatTime(msg.time)}</div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="message assistant">
                        <div className="message-avatar">🤖</div>
                        <div className="message-content">
                            <div className="typing-indicator">
                                <span /><span /><span />
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <div className="chat-input-area">
                <div className="chat-input-wrapper">
                    <input
                        className="chat-input"
                        placeholder="Type a message..."
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        id="chat-input"
                    />
                    <button className="chat-send-btn" onClick={sendMessage} disabled={!input.trim() || loading || streaming} id="chat-send">
                        ➤
                    </button>
                </div>
            </div>
        </div>
    )
}

// ─── Knowledge Base ───
function KnowledgeBase() {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState([])
    const [recent, setRecent] = useState([])
    const [searched, setSearched] = useState(false)

    useEffect(() => {
        fetchJSON('/api/memory?limit=20')
            .then(data => setRecent(data.memories || []))
            .catch(() => { })
    }, [])

    const handleSearch = async () => {
        if (!query.trim()) return
        setSearched(true)
        try {
            const data = await fetchJSON(`/api/memory/search?q=${encodeURIComponent(query)}&top_k=10`)
            setResults(data.results || [])
        } catch {
            setResults([])
        }
    }

    const displayItems = searched ? results : recent

    const formatDate = (timestamp) => {
        if (!timestamp) return ''
        return new Date(timestamp * 1000).toLocaleString()
    }

    return (
        <div className="kb-container">
            <div className="kb-search-wrapper">
                <input
                    className="kb-search-input"
                    placeholder="Semantic search across memories..."
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSearch()}
                    id="kb-search"
                />
                <button className="kb-search-btn" onClick={handleSearch} id="kb-search-btn">Search</button>
            </div>

            {displayItems.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">🧠</div>
                    <h3>{searched ? 'No results found' : 'Knowledge Base Empty'}</h3>
                    <p>{searched ? 'Try a different query' : 'Start chatting to build your knowledge base with vector embeddings'}</p>
                </div>
            ) : (
                displayItems.map((item, i) => (
                    <div className="kb-card" key={item.id || i}>
                        <div className="kb-card-header">
                            <span className="kb-card-type">
                                {item.metadata?.type || 'document'}
                            </span>
                            {item.distance !== undefined && item.distance !== null && (
                                <span className="kb-card-distance">
                                    similarity: {(1 - item.distance).toFixed(3)}
                                </span>
                            )}
                        </div>
                        <div className="kb-card-text">{item.text}</div>
                        <div className="kb-card-meta">
                            {formatDate(item.metadata?.timestamp)}
                        </div>
                    </div>
                ))
            )}
        </div>
    )
}

// ─── System Status ───
function SystemStatus() {
    const [status, setStatus] = useState(null)
    const [facts, setFacts] = useState({})

    useEffect(() => {
        fetchJSON('/api/status').then(setStatus).catch(() => { })
        fetchJSON('/api/facts').then(data => setFacts(data.facts || {})).catch(() => { })
    }, [])

    if (!status) {
        return (
            <div className="status-container">
                <div className="empty-state">
                    <div className="empty-state-icon">📊</div>
                    <h3>Loading status...</h3>
                    <p>Connecting to backend</p>
                </div>
            </div>
        )
    }

    return (
        <div className="status-container">
            <div className="status-card">
                <div className="status-card-icon blue">🧠</div>
                <h3>LLM Provider</h3>
                <div className="value">{status.llm_provider?.toUpperCase()}</div>
                <div className="sub">Active AI model</div>
            </div>

            <div className="status-card">
                <div className="status-card-icon purple">📦</div>
                <h3>Vector Memory</h3>
                <div className="value">{status.vector_memory?.total_documents ?? 0}</div>
                <div className="sub">Stored documents in ChromaDB</div>
            </div>

            <div className="status-card">
                <div className="status-card-icon green">🛠️</div>
                <h3>Registered Tools</h3>
                <div className="value">{status.tools_count}</div>
                <div className="tools-list">
                    {status.tools?.slice(0, 8).map(tool => (
                        <span className="tool-tag" key={tool}>{tool}</span>
                    ))}
                </div>
            </div>

            <div className="status-card">
                <div className="status-card-icon orange">💾</div>
                <h3>Stored Facts</h3>
                <div className="value">{Object.keys(facts).length}</div>
                <div className="sub">Key-value memories</div>
                <div className="tools-list" style={{ marginTop: '8px' }}>
                    {Object.entries(facts).slice(0, 6).map(([k, v]) => (
                        <span className="tool-tag" key={k}>{k}: {typeof v === 'string' ? v.slice(0, 30) : JSON.stringify(v).slice(0, 30)}</span>
                    ))}
                </div>
            </div>

            <div className="status-card">
                <div className="status-card-icon cyan">🌐</div>
                <h3>API Server</h3>
                <div className="value" style={{ color: 'var(--success)' }}>Online</div>
                <div className="sub">FastAPI v2.0.0 on port 8080</div>
            </div>

            <div className="status-card">
                <div className="status-card-icon blue">⚡</div>
                <h3>Architecture</h3>
                <div className="value" style={{ fontSize: '16px' }}>RAG + Vector DB</div>
                <div className="sub">ChromaDB + Semantic Search + Streaming</div>
            </div>
        </div>
    )
}

// ─── Header ───
function Header({ activeView }) {
    const titles = {
        chat: 'Chat',
        knowledge: 'Knowledge Base',
        status: 'System Status',
    }

    return (
        <header className="header">
            <h2 className="header-title">{titles[activeView] || 'Dashboard'}</h2>
            <div className="header-actions">
                <div className="header-badge">
                    ⚡ RAG Enabled
                </div>
                <div className="header-badge">
                    🧠 Vector Memory
                </div>
            </div>
        </header>
    )
}

// ─── App ───
export default function App() {
    const [activeView, setActiveView] = useState('chat')
    const [connected, setConnected] = useState(false)

    useEffect(() => {
        const checkConnection = async () => {
            try {
                const res = await fetch(`${API}/api/health`)
                setConnected(res.ok)
            } catch {
                setConnected(false)
            }
        }
        checkConnection()
        const interval = setInterval(checkConnection, 10000)
        return () => clearInterval(interval)
    }, [])

    const renderView = () => {
        switch (activeView) {
            case 'chat': return <ChatPanel />
            case 'knowledge': return <KnowledgeBase />
            case 'status': return <SystemStatus />
            default: return <ChatPanel />
        }
    }

    return (
        <div className="app-layout">
            <Sidebar activeView={activeView} setActiveView={setActiveView} connected={connected} />
            <main className="main-area">
                <Header activeView={activeView} />
                {renderView()}
            </main>
        </div>
    )
}
