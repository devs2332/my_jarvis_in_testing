import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { postJSON, fetchJSON } from '../utils/api';

const FALLBACK_MODELS = [
    { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', model: 'gpt-4o' },
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai', model: 'gpt-4o-mini' },
    { id: 'gemini-flash', name: 'Gemini 1.5 Flash', provider: 'google', model: 'gemini-1.5-flash' },
    { id: 'mistral-large', name: 'Mistral Large', provider: 'mistral', model: 'mistral-large-latest' },
    { id: 'llama-3-groq', name: 'Llama 3 (Groq)', provider: 'groq', model: 'llama-3.1-8b-instant' },
    { id: 'gpt-oss-openrouter', name: 'GPT-OSS 120B (Free)', provider: 'openrouter', model: 'openai/gpt-oss-120b' },
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
    const [availableModels, setAvailableModels] = useState(FALLBACK_MODELS);

    // Feature State
    const [selectedModel, setSelectedModel] = useState(FALLBACK_MODELS[4]); // Default to Groq
    const [searchMode, setSearchMode] = useState('none'); // 'none' | 'web_search' | 'deep_research'
    const [language, setLanguage] = useState('English');

    // UI State
    const [showModelMenu, setShowModelMenu] = useState(false);
    const [showLanguageMenu, setShowLanguageMenu] = useState(false); // New Dropdown State
    const [showPlusMenu, setShowPlusMenu] = useState(false);

    // Refs
    const messagesEndRef = useRef(null);
    const wsRef = useRef(null);
    const plusMenuRef = useRef(null);
    const modelMenuRef = useRef(null);
    const languageMenuRef = useRef(null);
    const recognitionRef = useRef(null);

    // Audio Streaming Refs
    const audioContextRef = useRef(null);
    const mediaStreamRef = useRef(null);
    const processorRef = useRef(null);

    // Fetch models from backend
    useEffect(() => {
        fetchJSON('/api/v1/models')
            .then(data => {
                if (data.models && data.models.length > 0) {
                    setAvailableModels(data.models);
                    // Try to keep current selection, or default to Groq-like
                    const groq = data.models.find(m => m.provider === 'groq');
                    if (groq) {
                        setSelectedModel(groq);
                        // Also sync this initial default to the backend
                        selectModel(groq);
                    }
                }
            })
            .catch(err => console.warn('Could not fetch models from backend, using fallback:', err));
    }, []);

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
            if (languageMenuRef.current && !languageMenuRef.current.contains(event.target)) {
                setShowLanguageMenu(false);
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
            fetchJSON('/api/history/' + chatId)
                .then(data => {
                    const found = data.conversation;
                    if (found) {
                        setHistory([
                            { role: 'user', content: found.user, time: new Date(found.timestamp * 1000) },
                            { role: 'assistant', content: found.jarvis, time: new Date(found.timestamp * 1000) }
                        ]);
                    } else {
                        console.warn("Chat ID not found in recent history:", chatId);
                    }
                })
                .catch(err => {
                    console.error("Failed to load chat history", err);
                    setHistory(null);
                })
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
                        // The server transcribed our voice, append it to the chat input box
                        setInput(prev => prev ? prev + ' ' + data.text : data.text);
                    } else if (data.type === 'info') {
                        console.log("Server Info:", data.text);
                    } else if (data.type === 'audio') {
                        const audio = new Audio("data:audio/mp3;base64," + data.data);
                        audio.play().catch(e => console.error("Audio play failed:", e));
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
    const toggleRecording = async () => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            alert("Waiting for server connection to activate microphone...");
            return;
        }

        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaStreamRef.current = stream;

                const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                audioContextRef.current = audioContext;

                const source = audioContext.createMediaStreamSource(stream);
                const processor = audioContext.createScriptProcessor(4096, 1, 1);
                processorRef.current = processor;

                source.connect(processor);
                processor.connect(audioContext.destination);

                processor.onaudioprocess = (e) => {
                    const floatData = e.inputBuffer.getChannelData(0);
                    const intData = new Int16Array(floatData.length);
                    for (let i = 0; i < floatData.length; i++) {
                        const s = Math.max(-1, Math.min(1, floatData[i]));
                        intData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                    }
                    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                        wsRef.current.send(intData.buffer);
                    }
                };

                setIsRecording(true);
                wsRef.current.send(JSON.stringify({
                    type: "voice_toggle",
                    active: true,
                    provider: selectedModel.provider,
                    model: selectedModel.model,
                    search_mode: searchMode,
                    language: language
                }));
            } catch (err) {
                console.error("Error accessing microphone:", err);
                alert("Could not access microphone.");
            }
        } else {
            if (processorRef.current) {
                processorRef.current.disconnect();
                processorRef.current = null;
            }
            if (audioContextRef.current) {
                audioContextRef.current.close();
                audioContextRef.current = null;
            }
            if (mediaStreamRef.current) {
                mediaStreamRef.current.getTracks().forEach(track => track.stop());
                mediaStreamRef.current = null;
            }

            setIsRecording(false);
            wsRef.current.send(JSON.stringify({
                type: "voice_toggle",
                active: false
            }));
        }
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
            search_mode: searchMode,
            research_mode: searchMode === 'deep_research',
            provider: selectedModel.provider,
            model: selectedModel.model,
            language: language
        };

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            setLoading(true);
            wsRef.current.send(JSON.stringify(payload));
        } else {
            // Fallback REST
            setLoading(true);
            try {
                const data = await postJSON('/api/v1/chat', payload);
                setMessages(prev => [...prev, { role: 'assistant', content: data.response, time: new Date() }]);
            } catch (e) {
                setMessages(prev => [...prev, { role: 'assistant', content: `Connection error: ${e.message}`, time: new Date() }]);
            }
            setLoading(false);
        }
    }, [input, loading, streaming, searchMode, selectedModel, chatId, navigate]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex-1 flex flex-col h-full relative bg-white dark:bg-[#0b1217] overflow-hidden">
            {/* Header */}
            <header className="h-[72px] flex items-center justify-between px-6 sticky top-0 bg-white/95 dark:bg-[#0b1217]/95 backdrop-blur-sm z-10 shrink-0 border-b border-gray-100 dark:border-slate-800">
                <div className="flex items-center gap-2 relative" ref={modelMenuRef}>
                    <button
                        onClick={() => setShowModelMenu(!showModelMenu)}
                        className="flex items-center gap-2 font-bold text-gray-800 dark:text-white text-xl hover:bg-gray-50 dark:hover:bg-slate-800 px-3 py-2 rounded-xl transition"
                    >
                        {selectedModel.name} <span className="material-icons text-gray-400 dark:text-slate-500 text-xl">keyboard_arrow_down</span>
                    </button>

                    {/* Model Dropdown */}
                    {showModelMenu && (
                        <div className="absolute top-full left-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-[0_4px_20px_-4px_rgba(0,0,0,0.15)] border border-gray-100 dark:border-slate-700 py-2 animate-in fade-in zoom-in-95 duration-100 font-display z-50">
                            <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">Select Model</div>
                            {availableModels.map(m => (
                                <button
                                    key={m.id}
                                    onClick={async () => {
                                        setSelectedModel(m);
                                        setShowModelMenu(false);
                                        try {
                                            await fetchJSON('/api/v1/models/active', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json' },
                                                body: JSON.stringify({
                                                    provider: m.provider,
                                                    model: m.model
                                                })
                                            });
                                        } catch (error) {
                                            console.error("Failed to set active model on backend:", error);
                                        }
                                    }}
                                    className={`w-full text-left px-4 py-2.5 text-sm flex items-center justify-between hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors
                                        ${selectedModel.id === m.id ? 'text-primary font-medium bg-primary/5' : 'text-gray-700 dark:text-slate-200'}`}
                                >
                                    {m.name}
                                    {selectedModel.id === m.id && <span className="material-icons text-sm text-primary">check</span>}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Right Side Header Items: Language + Actions */}
                <div className="flex items-center gap-3">
                    <div className="relative" ref={languageMenuRef}>
                        <button
                            onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                            className="flex items-center gap-1 text-[13px] font-semibold text-gray-500 dark:text-slate-400 hover:text-gray-800 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors px-3 py-1.5 rounded-lg"
                        >
                            {language === 'English' ? 'EN' : 'HI'} <span className="material-icons text-sm">expand_more</span>
                        </button>

                        {showLanguageMenu && (
                            <div className="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-xl shadow-[0_4px_20px_-4px_rgba(0,0,0,0.15)] border border-gray-100 dark:border-slate-700 py-2 animate-in fade-in zoom-in-95 duration-100 font-display z-50">
                                <div className="px-3 py-2 text-xs font-bold text-gray-400 uppercase tracking-wider">Select Language</div>
                                {['English', 'Hindi'].map(lang => (
                                    <button
                                        key={lang}
                                        onClick={() => {
                                            setLanguage(lang);
                                            setShowLanguageMenu(false);
                                        }}
                                        className={`w-full text-left px-4 py-2.5 text-sm flex items-center justify-between hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors
                                        ${language === lang ? 'text-primary font-medium bg-primary/5' : 'text-gray-700 dark:text-slate-200'}`}
                                    >
                                        {lang}
                                        {language === lang && <span className="material-icons text-sm text-primary">check</span>}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    <button className="w-10 h-10 flex flex-col items-center justify-center text-gray-400 hover:bg-gray-100 hover:text-gray-700 rounded-full transition" title="Share Chat">
                        <span className="material-icons text-xl">ios_share</span>
                    </button>
                    <button className="w-8 h-8 flex flex-col items-center justify-center bg-gray-400 text-white hover:bg-gray-500 rounded-full transition">
                        <span className="material-icons text-base font-bold">question_mark</span>
                    </button>
                </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto px-4 md:px-10 lg:px-24 xl:px-48 pt-4 pb-48 space-y-8">
                {(displayMessages || []).length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                        <div className="w-24 h-24 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-3xl flex items-center justify-center mb-6 shadow-xl shadow-blue-500/5 ring-1 ring-black/5 dark:ring-white/5">
                            <span className="material-icons text-5xl text-primary">smart_toy</span>
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
                            className={`flex ${msg.role === 'user' ? 'justify-end gap-3' : 'gap-4'} mt-2`}
                        >
                            {msg.role !== 'user' && (
                                <div className="w-8 h-8 rounded-full bg-primary flex flex-col items-center justify-center text-white shrink-0 shadow-sm mt-1">
                                    <span className="material-icons text-[18px]">smart_toy</span>
                                </div>
                            )}

                            <div className={`flex flex-col ${msg.role === 'user' ? 'items-end flex-1' : 'flex-1 min-w-0'} max-w-[85%] lg:max-w-[80%]`}>
                                {msg.role === 'user' ? (
                                    <div className="text-sm font-bold text-gray-800 dark:text-slate-200 mb-1 mr-2">You</div>
                                ) : (
                                    <div className="flex items-center gap-2 mb-1 h-[24px]">
                                        <span className="font-bold text-gray-900 dark:text-white text-sm">Jarvis</span>
                                        <span className="bg-[#f3f4f6] dark:bg-slate-800 text-gray-500 dark:text-slate-400 text-[10px] font-bold px-2 py-0.5 rounded border border-gray-200 dark:border-slate-700">v4.0</span>
                                    </div>
                                )}

                                <div className={`${msg.role === 'user' ? 'bg-[#f3f4f6] dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-3xl rounded-tr-sm px-6 py-4' : 'bg-[#f9fafb] dark:bg-[#151b26] border border-gray-100 dark:border-slate-800 shadow-sm rounded-3xl rounded-tl-sm px-6 py-4 text-gray-800 dark:text-slate-200 w-full overflow-x-auto'} text-base leading-relaxed`}>
                                    <div className="markdown-content">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                code({ node, inline, className, children, ...props }) {
                                                    const match = /language-(\w+)/.exec(className || '')
                                                    return !inline && match ? (
                                                        <div className="rounded-lg overflow-hidden my-2 border border-slate-200 bg-[#0d1117]">
                                                            <div className="flex items-center justify-between px-3 py-1.5 bg-slate-800/50 border-b border-slate-700 text-xs text-slate-500 font-mono">
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
                                                        <code className={`${className} bg-slate-100 px-1 py-0.5 rounded text-pink-500 font-mono text-xs`} {...props}>
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
                            </div>

                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-orange-100 overflow-hidden flex items-center justify-center shrink-0 mt-1">
                                    <img src="https://api.dicebear.com/7.x/notionists/svg?seed=Sarah&backgroundColor=ffe0b2" alt="User" className="w-full h-full object-cover" />
                                </div>
                            )}
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
            <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-white dark:from-[#0b1217] via-white/95 dark:via-[#0b1217]/95 to-transparent pt-12 pb-6 px-4 md:px-10 lg:px-24 xl:px-48 z-20">
                <div className="relative bg-white dark:bg-[#151b26] border border-gray-200 dark:border-slate-700 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.08),0_1px_4px_-1px_rgba(0,0,0,0.05)] dark:shadow-black/30 rounded-[2rem] p-2 flex items-center transition-shadow focus-within:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.1)] focus-within:border-gray-300 dark:focus-within:border-slate-600 group">

                    {/* Left Action Buttons */}
                    <div className="flex items-center gap-1 ml-1 pr-2 relative" ref={plusMenuRef}>
                        <button
                            onClick={() => setShowPlusMenu(!showPlusMenu)}
                            className={`w-10 h-10 flex flex-col items-center justify-center rounded-full transition shrink-0 ${showPlusMenu ? 'text-primary bg-primary/10' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'}`}
                            title="Features"
                        >
                            <span className="material-icons text-[24px]">add</span>
                        </button>

                        {/* Plus Menu Popover */}
                        {showPlusMenu && (
                            <div className="absolute bottom-full left-0 mb-3 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-gray-100 dark:border-slate-700 p-2 animate-in fade-in zoom-in-95 duration-100 z-50">
                                <div className="px-3 py-2 text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wider">Search Mode</div>

                                <label className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 cursor-pointer transition-colors"
                                    onClick={() => setSearchMode(searchMode === 'web_search' ? 'none' : 'web_search')}
                                >
                                    <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${searchMode === 'web_search' ? 'bg-primary border-primary' : 'border-gray-300 dark:border-slate-500'}`}>
                                        {searchMode === 'web_search' && <span className="material-icons text-[10px] text-white font-bold">check</span>}
                                    </div>
                                    <span className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-slate-200">
                                        <span className="material-icons text-[16px]">search</span> Web Search
                                    </span>
                                </label>

                                <label className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 cursor-pointer transition-colors"
                                    onClick={() => setSearchMode(searchMode === 'deep_research' ? 'none' : 'deep_research')}
                                >
                                    <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${searchMode === 'deep_research' ? 'bg-primary border-primary' : 'border-gray-300 dark:border-slate-500'}`}>
                                        {searchMode === 'deep_research' && <span className="material-icons text-[10px] text-white font-bold">check</span>}
                                    </div>
                                    <span className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-slate-200">
                                        <span className="material-icons text-[16px]">travel_explore</span> Deep Research
                                    </span>
                                </label>
                            </div>
                        )}

                        <button
                            onClick={toggleRecording}
                            className={`w-10 h-10 flex flex-col items-center justify-center rounded-full transition shrink-0 ${isRecording ? 'text-white bg-red-500 animate-pulse' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'}`}
                            title={isRecording ? "Stop Recording" : "Start Voice"}
                        >
                            <span className="material-icons text-[22px]">mic</span>
                        </button>
                    </div>

                    {/* Input Textarea */}
                    <textarea
                        className="flex-1 max-h-32 min-h-[24px] bg-transparent outline-none resize-none px-2 py-3 text-gray-800 dark:text-slate-200 placeholder-gray-400 dark:placeholder-slate-500 text-[15px] leading-snug"
                        placeholder={searchMode === 'deep_research' ? "Ask something complex (Deep Research)..." : searchMode === 'web_search' ? "Search the web..." : "Message Jarvis..."}
                        rows={1}
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                    />

                    {/* Send Button */}
                    <button
                        className={`w-10 h-10 mt-auto rounded-full transition shrink-0 ml-2 mr-1 flex flex-col items-center justify-center ${!input.trim() || loading || streaming ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-primary text-white hover:bg-primary-hover shadow-sm'}`}
                        onClick={() => sendMessage()}
                        disabled={!input.trim() || loading || streaming}
                    >
                        <span className="material-icons text-xl leading-none font-bold">arrow_upward</span>
                    </button>
                </div>

                {/* Status / Disclaimer Text */}
                <div className="text-center mt-3 flex items-center justify-center gap-3">
                    {searchMode === 'web_search' && (
                        <span className="text-[10px] font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full flex items-center gap-1">
                            <span className="material-icons text-[10px]">search</span> WEB SEARCH
                        </span>
                    )}
                    {searchMode === 'deep_research' && (
                        <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full flex items-center gap-1">
                            <span className="material-icons text-[10px]">travel_explore</span> DEEP RESEARCH
                        </span>
                    )}
                    <div className="text-xs text-gray-400 font-medium tracking-tight">
                        Jarvis can make mistakes. Consider checking important information.
                    </div>
                </div>
            </div>
        </div>
    );
}
