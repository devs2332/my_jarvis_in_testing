import React, { useState, useEffect, useRef, useCallback } from 'react'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { fetchJSON, postJSON } from './utils/api';

import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import SystemStatus from './components/SystemStatus'
import KnowledgeBase from './components/KnowledgeBase'
import Settings from './components/Settings'
import HistorySearch from './components/HistorySearch'
import Trash from './components/Trash'
import UserProfile from './components/UserProfile'

// ─── Main App Component ───
function AppContent() {
    const location = useLocation();
    const [connected, setConnected] = useState(false)
    const [activeView, setActiveView] = useState('chat') // Kept for legacy prop if needed, but router drives view now.

    // Chat State (Lifted or specialized? For now we keep main chat logic here to avoid huge refactor, 
    // but ideally ChatPanel should handle its own state or use a Context)
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const [systemStatus, setSystemStatus] = useState({})

    // Refs
    const ws = useRef(null)
    const messagesEndRef = useRef(null)

    // ─── WebSocket & Init ───
    useEffect(() => {
        const connectWebSocket = () => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            // Use window.location.host to respect the proxy
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            ws.current = new WebSocket(wsUrl);

            ws.current.onopen = () => {
                setConnected(true);
                console.log('WebSocket Connected');
                // Request initial status
                if (ws.current.readyState === WebSocket.OPEN) {
                    ws.current.send(JSON.stringify({ type: 'get_status' }));
                }
            };

            ws.current.onclose = () => {
                setConnected(false);
                setTimeout(connectWebSocket, 3000);
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                } catch (e) {
                    console.error("WS Parse Error", e);
                }
            };
        };

        connectWebSocket();

        // Initial Load
        loadHistory();

        return () => ws.current?.close();
    }, []);

    const handleWebSocketMessage = (data) => {
        if (data.type === 'status_update') {
            setSystemStatus(data.payload);
        } else if (data.type === 'message_chunk') {
            setMessages(prev => {
                const last = prev[prev.length - 1];
                if (last && last.role === 'assistant' && last.id === data.id) {
                    // Update existing message
                    return prev.map(msg => msg.id === data.id ? { ...msg, content: msg.content + data.content } : msg);
                } else {
                    // This shouldn't happen often if we create the placeholder first, but just in case
                    return [...prev, { role: 'assistant', content: data.content, id: data.id }];
                }
            });
        } else if (data.type === 'message_complete') {
            setIsTyping(false);
        }
    };

    const loadHistory = async () => {
        try {
            const history = await fetchJSON('/api/history');
            // Transform if necessary, or just set
            // API likely returns list of conversations, for this simple view we might just load current?
            // For now assuming empty or we just start fresh in this view.
        } catch (err) {
            console.error("Failed to load history", err);
        }
    };

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input, id: Date.now() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        // Create placeholder for assistant
        const assistantMsgId = Date.now() + 1;
        setMessages(prev => [...prev, { role: 'assistant', content: '', id: assistantMsgId }]);

        try {
            // We use standard fetch for sending, WS for streaming response
            await postJSON('/api/chat', { message: input, id: assistantMsgId });
        } catch (err) {
            console.error("Send failed", err);
            setMessages(prev => [...prev, { role: 'system', content: `Error: ${err.message}` }]);
            setIsTyping(false);
        }
    };

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);


    // Sidebar State
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

    return (
        <div className="flex h-screen bg-background-light dark:bg-background-dark overflow-hidden font-display text-slate-800 dark:text-slate-100">
            <Sidebar
                connected={connected}
                isCollapsed={isSidebarCollapsed}
                toggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            />

            <main className={`flex-1 flex flex-col min-w-0 bg-white/50 dark:bg-[#0b1217] transition-all duration-300`}>
                <Routes>
                    <Route path="/" element={
                        <ChatPanel
                            messages={messages}
                            input={input}
                            setInput={setInput}
                            sendMessage={sendMessage}
                            isTyping={isTyping}
                            messagesEndRef={messagesEndRef}
                        />
                    } />
                    {/* Route for loading specific history chats */}
                    <Route path="/c/:chatId" element={
                        <ChatPanel
                            messages={messages}
                            input={input}
                            setInput={setInput}
                            sendMessage={sendMessage}
                            isTyping={isTyping}
                            messagesEndRef={messagesEndRef}
                        />
                    } />
                    <Route path="/knowledge" element={<KnowledgeBase />} />
                    <Route path="/status" element={<SystemStatus status={systemStatus} />} />

                    {/* New Routes */}
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/history" element={<HistorySearch />} />
                    <Route path="/trash" element={<Trash />} />
                    <Route path="/profile" element={<UserProfile />} />
                </Routes>
            </main>
        </div>
    )
}

// ... (imports remain)

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({ error, errorInfo });
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-8 bg-slate-900 text-white h-screen overflow-auto">
                    <h1 className="text-2xl font-bold mb-4 text-red-500">Something went wrong.</h1>
                    <details className="whitespace-pre-wrap font-mono text-sm bg-slate-800 p-4 rounded">
                        {this.state.error && this.state.error.toString()}
                        <br />
                        {this.state.errorInfo && this.state.errorInfo.componentStack}
                    </details>
                </div>
            );
        }
        return this.props.children;
    }
}

// ... (AppContent remains same)

export default function App() {
    return (
        <ErrorBoundary>
            <BrowserRouter>
                <AppContent />
            </BrowserRouter>
        </ErrorBoundary>
    );
}
