import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { postJSON, fetchJSON } from '../utils/api';

const AVAILABLE_MODELS = [
    { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', model: 'gpt-4o' },
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai', model: 'gpt-4o-mini' },
    { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'google', model: 'gemini-1.5-flash' },
    { id: 'mistral-large', name: 'Mistral Large', provider: 'mistral', model: 'mistral-large-latest' },
    { id: 'llama-3-groq', name: 'Llama 3 (Groq)', provider: 'groq', model: 'llama-3.1-8b-instant' },
    { id: 'gpt-oss-120b', name: 'GPT-OSS 120B (Free)', provider: 'openrouter', model: 'openai/gpt-oss-120b' },
    { id: 'gpt-oss-nvidia', name: 'GPT-OSS 120B (NVIDIA)', provider: 'nvidia', model: 'openai/gpt-oss-120b' },
];

export default function ChatPanel() {
    // Router hooks
    const { chatId } = useParams();
    const navigate = useNavigate();

    // Local State
    const [messages, setMessages] = useState([]);
    const [history, setHistory] = useState(null);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [streaming, setStreaming] = useState(false);
    const [isRecording, setIsRecording] = useState(false);

    // Feature State
    const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[4]); // Default to Groq (Index 4)
    const [isResearchMode, setIsResearchMode] = useState(false);

    // UI State
    const [showModelMenu, setShowModelMenu] = useState(false);
    const [showPlusMenu, setShowPlusMenu] = useState(false);

    // Refs
    const messagesEndRef = useRef(null);
    const wsRef = useRef(null);
    const plusMenuRef = useRef(null);
    const modelMenuRef = useRef(null);
    const recognitionRef = useRef(null);

    // Calculate display messages (Local messages OR History)
    // CRITICAL: This variable must be defined before use
    const displayMessages = (chatId && history) ? history : messages;

    // Scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [displayMessages, loading, streaming]);

    // Close menus on outside click
    useEffect(() => {
        function handleClickOutside(event) {
            if (plusMenuRef.current && !plusMenuRef.current.contains(event.target)) {
                setShowPlusMenu(false);
            }
            if (modelMenuRef.current && !modelMenuRef.current.contains(event.target)) {
                setShowModelMenu(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // Load History if chatId is present
    useEffect(() => {
        if (chatId) {
            setLoading(true);
            setHistory(null); // Clear previous history view while loading
            fetchJSON('/api/history?limit=100')
                .then(data => {
                    const found = (data.conversations || []).find(c => c.id === chatId);
                    if (found) {
                        setHistory([
                            { role: 'user', content: found.user, time: new Date(found.timestamp * 1000) },
                            { role: 'assistant', content: found.jarvis, time: new Date(found.timestamp * 1000) }
                        ]);
                    } else {
                        console.warn("Chat ID not found in recent history:", chatId);
                    }
                })
                .catch(err => console.error("Failed to load chat history", err))
                .finally(() => setLoading(false));
        } else {
            setHistory(null);
        }
    }, [chatId]);

    // WebSocket Connection
    useEffect(() => {
        const connectWS = () => {
            // Logic to determine WS URL
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            // Use window.location.host to respect the proxy (e.g., localhost:5173 -> localhost:8080 via Vite)
            const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

            console.log('Connecting to Chat WS:', wsUrl);
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('Chat WS Connected');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'thinking') {
                        setLoading(true);
                    } else if (data.type === 'token') {
                        setStreaming(true);
                        setLoading(false);
                        setMessages(prev => {
                            const last = prev[prev.length - 1];
                            if (last && last.role === 'assistant' && last.streaming) {
                                return [
                                    ...prev.slice(0, -1),
                                    { ...last, content: last.content + data.text }
                                ];
                            }
                            return [...prev, { role: 'assistant', content: data.text, streaming: true, time: new Date() }];
                        });
                    } else if (data.type === 'complete') {
                        setStreaming(false);
                        setLoading(false);
                        setMessages(prev => {
                            const last = prev[prev.length - 1];
                            if (last && last.role === 'assistant' && last.streaming) {
                                return [
                                    ...prev.slice(0, -1),
                                    { ...last, content: data.text, streaming: false }
                                ];
                            }
                            return [...prev, { role: 'assistant', content: data.text, time: new Date() }];
                        });
                    } else if (data.type === 'user_voice_echo') {
                        // The server transcribed our voice, add it to the chat as our own message!
                        setMessages(prev => [...prev, { role: 'user', content: data.text, time: new Date() }]);
                    } else if (data.type === 'info') {
                        console.log("Server Info:", data.text);
                    }
                } catch (e) {
                    console.error("WS Message Parse Error", e);
                }
            };

            ws.onclose = () => {
                console.log('Chat WS Closed, retrying...');
                setTimeout(connectWS, 3000);
            };

            ws.onerror = (err) => {
                console.error('Chat WS Error:', err);
            };
        };

        connectWS();
        return () => wsRef.current?.close();
    }, []);

    // Toggle Backend Voice Manager
    const toggleRecording = () => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            alert("Waiting for server connection to activate microphone...");
            return;
        }

        const newState = !isRecording;
        setIsRecording(newState);

        wsRef.current.send(JSON.stringify({
            type: "voice_toggle",
            active: newState
        }));
    };

    // Send Message Handler
    const sendMessage = useCallback(async (text = input) => {
        const msgText = typeof text === 'string' ? text : input;
        if (!msgText.trim() || loading || streaming) return;

        const userMsg = msgText.trim();
        setInput('');

        // If we are viewing history, start a new chat (clear history view)
        if (chatId) {
            navigate('/'); // Reset URL to root for new chat
            setHistory(null);
            setMessages([{ role: 'user', content: userMsg, time: new Date() }]);
        } else {
            setMessages(prev => [...prev, { role: 'user', content: userMsg, time: new Date() }]);
        }

        const payload = {
            message: userMsg,
            research_mode: isResearchMode,
            provider: selectedModel.provider,
            model: selectedModel.model
        };

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            setLoading(true);
            wsRef.current.send(JSON.stringify(payload));
        } else {
            // Fallback REST
            setLoading(true);
            try {
                const data = await postJSON('/api/chat', payload);
                setMessages(prev => [...prev, { role: 'assistant', content: data.response, time: new Date() }]);
            } catch (e) {
                setMessages(prev => [...prev, { role: 'assistant', content: `Connection error: ${e.message}`, time: new Date() }]);
            }
            setLoading(false);
        }
    }, [input, loading, streaming, isResearchMode, selectedModel, chatId, navigate]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex-1 flex flex-col h-full relative bg-background-light dark:bg-background-dark overflow-hidden">
            {/* Header */}
            <header className="h-16 flex items-center justify-between px-6 border-b border-transparent shrink-0 z-20">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 relative" ref={modelMenuRef}>
                    <span className="text-sm font-medium">Model:</span>
                    <button
                        onClick={() => setShowModelMenu(!showModelMenu)}
                        className="flex items-center gap-1 text-sm font-semibold text-slate-800 dark:text-white hover:text-primary transition-colors bg-white dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-primary/50"
                    >
                        {selectedModel.name} <span className="material-icons text-base">expand_more</span>
                    </button>

                    {/* Model Dropdown */}
                    {showModelMenu && (
                        <div className="absolute top-full left-10 mt-2 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-100 dark:border-slate-700 py-2 animate-in fade-in zoom-in-95 duration-100 font-display z-50">
                            <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">Select Model</div>
                            {AVAILABLE_MODELS.map(m => (
                                <button
                                    key={m.id}
                                    onClick={() => {
                                        setSelectedModel(m);
                                        setShowModelMenu(false);
                                    }}
                                    className={`w-full text-left px-4 py-2.5 text-sm flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors
                                        ${selectedModel.id === m.id ? 'text-primary font-medium bg-primary/5' : 'text-slate-700 dark:text-slate-200'}`}
                                >
                                    {m.name}
                                    {selectedModel.id === m.id && <span className="material-icons text-sm text-primary">check</span>}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    <button className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Share Chat">
                        <span className="material-icons text-[20px]">ios_share</span>
                    </button>
                </div>
            </header>

            {/* Chat Area — pb-40 ensures content isn't hidden behind the fixed input bar */}
            <div className="flex-1 overflow-y-auto p-4 pb-40 space-y-6">
                {(displayMessages || []).length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center opacity-0 animate-fadeIn" style={{ opacity: 1, animationFillMode: 'forwards' }}>
                        <div className="w-24 h-24 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-3xl flex items-center justify-center mb-6 shadow-xl shadow-blue-500/5 ring-1 ring-black/5 dark:ring-white/5">
                            <span className="material-icons text-5xl text-primary bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-500">smart_toy</span>
                        </div>
                        <h2 className="text-3xl font-bold text-slate-800 dark:text-slate-100 mb-3 tracking-tight">
                            How can I help you?
                        </h2>
                        <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto text-lg leading-relaxed">
                            I'm ready to assist with your tasks, answer questions, or generate code.
                        </p>
                    </div>
                ) : (
                    (displayMessages || []).map((msg, index) => (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                            key={index}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`max-w-[85%] lg:max-w-[75%] rounded-2xl p-4 shadow-sm backdrop-blur-sm
                            ${msg.role === 'user'
                                    ? 'bg-primary text-white ml-12 rounded-tr-sm'
                                    : 'bg-white/80 dark:bg-[#1e2936]/90 border border-slate-200 dark:border-slate-700/50 mr-12 rounded-tl-sm text-slate-800 dark:text-slate-200'
                                }`}
                            >
                                <div className="markdown-content text-sm leading-relaxed">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            code({ node, inline, className, children, ...props }) {
                                                const match = /language-(\w+)/.exec(className || '')
                                                return !inline && match ? (
                                                    <div className="rounded-lg overflow-hidden my-2 border border-slate-200 dark:border-slate-700 bg-[#0d1117]">
                                                        <div className="flex items-center justify-between px-3 py-1.5 bg-slate-100 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700 text-xs text-slate-500 font-mono">
                                                            <span>{match[1]}</span>
                                                            <button className="hover:text-primary transition-colors">Copy</button>
                                                        </div>
                                                        <pre className="p-3 overflow-x-auto bg-[#0d1117] text-slate-300 scrollbar-thin scrollbar-thumb-slate-700">
                                                            <code className={className} {...props}>
                                                                {children}
                                                            </code>
                                                        </pre>
                                                    </div>
                                                ) : (
                                                    <code className={`${className} bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-pink-500 font-mono text-xs`} {...props}>
                                                        {children}
                                                    </code>
                                                )
                                            }
                                        }}
                                    >
                                        {String(msg.content || '')}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        </motion.div>
                    ))
                )}

                {/* Typing Indicator */}
                {(loading || streaming) && (
                    <div className="flex justify-start">
                        <div className="bg-white/80 dark:bg-[#1e2936]/90 border border-slate-200 dark:border-slate-700/50 rounded-2xl p-4 shadow-sm mr-12 rounded-tl-sm flex gap-1.5 items-center h-12">
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-background-light via-background-light to-transparent dark:from-background-dark dark:via-background-dark pt-10 pb-6 px-4">
                <div className="max-w-3xl mx-auto">
                    <div className="relative group">
                        {/* Glow effect */}
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/30 to-purple-500/30 rounded-xl opacity-0 group-focus-within:opacity-100 transition duration-500 blur"></div>

                        <div className="relative flex items-end gap-2 bg-white dark:bg-[#1a2c36] shadow-lg dark:shadow-black/20 rounded-xl border border-slate-200 dark:border-slate-700 overflow-visible p-2 transition-colors">

                            {/* Plus Menu Button */}
                            <div className="relative flex flex-col justify-end mb-[2px]" ref={plusMenuRef}>
                                <button
                                    onClick={() => setShowPlusMenu(!showPlusMenu)}
                                    className={`p-2 rounded-lg transition-colors ${showPlusMenu ? 'text-primary bg-primary/10' : 'text-slate-400 hover:text-primary hover:bg-slate-50 dark:hover:bg-slate-800'}`}
                                >
                                    <span className="material-icons text-xl">add_circle_outline</span>
                                </button>

                                {/* Plus Menu Popover */}
                                {showPlusMenu && (
                                    <div className="absolute bottom-full left-0 mb-3 w-48 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-100 dark:border-slate-700 p-2 animate-in fade-in zoom-in-95 duration-100 mb-2 z-50">
                                        <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">Features</div>

                                        <label className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer transition-colors">
                                            <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${isResearchMode ? 'bg-primary border-primary' : 'border-slate-400'}`}>
                                                {isResearchMode && <span className="material-icons text-[10px] text-white font-bold">check</span>}
                                            </div>
                                            <input type="checkbox" className="hidden" checked={isResearchMode} onChange={() => setIsResearchMode(!isResearchMode)} />
                                            <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Deep Research</span>
                                        </label>


                                    </div>
                                )}
                            </div>

                            <textarea
                                className="w-full bg-transparent border-none focus:ring-0 resize-none py-3 text-slate-800 dark:text-slate-100 placeholder-slate-400 max-h-48 overflow-y-auto outline-none"
                                placeholder={isResearchMode ? "Ask something complex (Research On)..." : "Type a message..."}
                                rows={1}
                                style={{ minHeight: '44px' }}
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                            />

                            <button
                                className={`p-2 mb-[2px] rounded-lg shadow-sm hover:shadow transition-all duration-200 self-end mr-1 ${isRecording
                                    ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                                    : 'bg-slate-100 hover:bg-slate-200 text-slate-500 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-400'
                                    }`}
                                onClick={toggleRecording}
                                title={isRecording ? "Stop Recording" : "Start Recording"}
                            >
                                <span className="material-icons text-lg leading-none pt-0.5">mic</span>
                            </button>

                            <button
                                className={`p-2 mb-[2px] rounded-lg shadow-sm hover:shadow transition-all duration-200 self-end ${!input.trim() || loading || streaming
                                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed dark:bg-slate-700 dark:text-slate-500'
                                    : 'bg-primary hover:bg-[#2390c6] text-white'
                                    }`}
                                onClick={() => sendMessage()}
                                disabled={!input.trim() || loading || streaming}
                            >
                                <span className="material-icons text-lg leading-none pt-0.5">arrow_upward</span>
                            </button>
                        </div>
                    </div>
                    <div className="text-center mt-3 flex items-center justify-center gap-3">
                        {/* Status Indicators */}
                        {isResearchMode && (
                            <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full flex items-center gap-1">
                                <span className="material-icons text-[10px]">travel_explore</span> RESEARCH ON
                            </span>
                        )}
                        {!isResearchMode && (
                            <p className="text-[11px] text-slate-400 dark:text-slate-500">
                                AI may produce inaccurate information about people, places, or facts.
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
