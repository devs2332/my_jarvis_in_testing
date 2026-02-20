import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { fetchJSON, deleteJSON } from '../utils/api';

export default function HistorySearch() {
    const navigate = useNavigate();
    const location = useLocation();
    const [searchQuery, setSearchQuery] = useState("");
    const [filter, setFilter] = useState("All");
    const [historyItems, setHistoryItems] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // Reload history every time the page is navigated to
    useEffect(() => {
        loadHistory();
    }, [location.key]);

    // Also reload when the browser tab becomes visible again
    useEffect(() => {
        const handleVisibility = () => {
            if (document.visibilityState === 'visible') loadHistory();
        };
        document.addEventListener('visibilitychange', handleVisibility);
        return () => document.removeEventListener('visibilitychange', handleVisibility);
    }, []);

    const loadHistory = async () => {
        setIsLoading(true);
        try {
            const data = await fetchJSON('/api/history?limit=100');
            // Transform data if needed, backend returns list of {user, jarvis, id, timestamp}
            const formatted = (data.conversations || []).map(item => ({
                id: item.id || Math.random().toString(),
                title: item.user || "Conversation",
                preview: item.jarvis ? item.jarvis.substring(0, 120) + "..." : "No response",
                time: item.datetime || (item.timestamp ? new Date(item.timestamp * 1000).toLocaleString() : "Unknown"),
                type: item.fast_mode ? 'fast' : item.research_mode ? 'research' : 'chat',
                starred: false,
                raw_time: item.timestamp,
                // New metadata
                model: item.model || null,
                provider: item.provider || null,
                fast_mode: item.fast_mode || false,
                research_mode: item.research_mode || false,
                language: item.language || "English",
                response_length: item.response_length || 0,
            }));
            setHistoryItems(formatted);
        } catch (error) {
            console.error("Failed to load history:", error);
            setHistoryItems([]);
        } finally {
            setIsLoading(false);
        }
    };

    const deleteItem = async (e, id) => {
        e.stopPropagation();
        if (window.confirm("Move this conversation to trash?")) {
            try {
                await deleteJSON(`/api/history/${id}`);
                setHistoryItems(prev => prev.filter(item => item.id !== id));
            } catch (error) {
                console.error("Delete failed", error);
                alert("Delete failed: " + error.message);
            }
        }
    };

    // Filter Logic
    const filteredItems = historyItems.filter(item => {
        const titleMatch = (item.title || "").toLowerCase().includes(searchQuery.toLowerCase());
        const previewMatch = (item.preview || "").toLowerCase().includes(searchQuery.toLowerCase());

        const matchesSearch = titleMatch || previewMatch;
        const matchesFilter = filter === 'All'
            ? true
            : filter === 'Starred' ? item.starred : item.type === filter.toLowerCase();
        return matchesSearch && matchesFilter;
    });



    return (
        <div className="flex-1 flex flex-col h-[calc(100vh-theme(spacing.16))] relative bg-slate-50/50 dark:bg-[#0b1217] font-display">
            {/* Header */}
            <header className="flex items-center justify-between px-8 py-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0b1217] z-10 shrink-0">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-50 dark:bg-indigo-900/10 rounded-lg text-indigo-500">
                        <span className="material-icons text-2xl">history</span>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-slate-900 dark:text-white">History</h1>
                        <p className="text-sm text-slate-500 dark:text-slate-400">View your past conversations</p>
                    </div>
                </div>
                <div className="flex items-center gap-3 w-full max-w-md">
                    <div className="relative flex-1 group">
                        <span className="material-icons absolute left-3 top-2.5 text-slate-400 group-focus-within:text-primary transition-colors">search</span>
                        <input
                            type="text"
                            placeholder="Search history..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 bg-slate-100 dark:bg-[#151b26] border-none rounded-xl text-sm focus:ring-2 focus:ring-primary/20 focus:bg-white dark:focus:bg-[#1a222c] transition-all outline-none"
                        />
                    </div>
                    {/* Filters */}
                    <div className="flex bg-slate-100 dark:bg-[#151b26] p-1 rounded-lg shrink-0">
                        {['All', 'Starred'].map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${filter === f ? 'bg-white dark:bg-slate-700 shadow-sm text-primary' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}
                            >
                                {f}
                            </button>
                        ))}
                    </div>
                </div>
            </header>

            {/* Content */}
            <div className="flex-1 overflow-y-auto px-8 py-6">
                {isLoading ? (
                    <div className="flex justify-center items-center h-40">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                ) : filteredItems.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full pb-20 opacity-0 animate-fadeIn" style={{ opacity: 1 }}>
                        <div className="w-20 h-20 bg-slate-100 dark:bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-300 dark:text-slate-600">
                            <span className="material-icons text-5xl">manage_search</span>
                        </div>
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white">No matches found</h3>
                        <p className="text-slate-500 dark:text-slate-400 max-w-xs mt-2 text-center text-sm">
                            Try adjusting your filters or search for something else.
                        </p>
                    </div>
                ) : (
                    <div className="max-w-5xl mx-auto space-y-3">
                        <AnimatePresence>
                            {filteredItems.map((item) => (
                                <motion.div
                                    key={item.id}
                                    layout
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    whileHover={{ scale: 1.005, backgroundColor: "rgba(var(--color-surface-hover), 0.5)" }}
                                    onClick={() => navigate(`/c/${item.id}`)}
                                    className="group relative bg-white dark:bg-[#151b26] border border-slate-200 dark:border-slate-800 rounded-xl p-4 cursor-pointer hover:border-primary/30 hover:shadow-md dark:hover:shadow-black/20 transition-all duration-200"
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex items-start gap-4 overflow-hidden">
                                            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${item.type === 'research' ? 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400' :
                                                item.type === 'fast' ? 'bg-amber-100 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400' :
                                                    'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                                }`}>
                                                <span className="material-icons text-xl">
                                                    {item.type === 'research' ? 'science' : item.type === 'fast' ? 'bolt' : 'chat_bubble_outline'}
                                                </span>
                                            </div>
                                            <div className="min-w-0 flex-1">
                                                <h4 className="font-semibold text-slate-900 dark:text-slate-100 truncate pr-8 group-hover:text-primary transition-colors">{item.title}</h4>
                                                <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2 mt-1 leading-relaxed">{item.preview}</p>
                                                {/* Metadata Badges */}
                                                <div className="flex flex-wrap items-center gap-1.5 mt-2">
                                                    {item.model && (
                                                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 border border-blue-200/50 dark:border-blue-800/30">
                                                            <span className="material-icons" style={{ fontSize: '11px' }}>smart_toy</span>
                                                            {item.model}
                                                        </span>
                                                    )}
                                                    {item.provider && (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                                                            {item.provider}
                                                        </span>
                                                    )}
                                                    {item.research_mode && (
                                                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400 border border-green-200/50 dark:border-green-800/30">
                                                            <span className="material-icons" style={{ fontSize: '11px' }}>science</span>
                                                            Research
                                                        </span>
                                                    )}
                                                    {item.fast_mode && (
                                                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400 border border-amber-200/50 dark:border-amber-800/30">
                                                            <span className="material-icons" style={{ fontSize: '11px' }}>bolt</span>
                                                            Fast
                                                        </span>
                                                    )}
                                                    {item.language && item.language !== "English" && (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400 border border-purple-200/50 dark:border-purple-800/30">
                                                            {item.language}
                                                        </span>
                                                    )}
                                                    {item.response_length > 0 && (
                                                        <span className="text-[10px] text-slate-400 dark:text-slate-500 ml-1">
                                                            {item.response_length > 1000 ? `${(item.response_length / 1000).toFixed(1)}k` : item.response_length} chars
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end gap-2 pl-2 shrink-0">
                                            <span className="text-xs text-slate-400 whitespace-nowrap">{item.time}</span>
                                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity translate-x-2 group-hover:translate-x-0 duration-200">
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); /* toggle star */ }}
                                                    className={`p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ${item.starred ? 'text-amber-400' : 'text-slate-400'}`}
                                                >
                                                    <span className="material-icons text-lg">{item.starred ? 'star' : 'star_border'}</span>
                                                </button>
                                                <button
                                                    onClick={(e) => deleteItem(e, item.id)}
                                                    className="p-1.5 rounded-md hover:bg-red-50 text-slate-400 hover:text-red-500 dark:hover:bg-red-900/20 transition-colors"
                                                >
                                                    <span className="material-icons text-lg">delete_outline</span>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </div>
        </div>
    );
}
