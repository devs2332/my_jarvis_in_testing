import React, { useState, useEffect } from 'react';
import { fetchJSON } from '../utils/api';

export default function KnowledgeBase() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [recent, setRecent] = useState([]);
    const [searched, setSearched] = useState(false);

    useEffect(() => {
        fetchJSON('/api/v1/memory?limit=20')
            .then(data => setRecent(data.memories || []))
            .catch(() => { });
    }, []);

    const handleSearch = async () => {
        if (!query.trim()) return;
        setSearched(true);
        try {
            const data = await fetchJSON(`/api/v1/memory/search?q=${encodeURIComponent(query)}&top_k=10`);
            setResults(data.results || []);
        } catch {
            setResults([]);
        }
    };

    const displayItems = searched ? results : recent;

    const formatDate = (timestamp) => {
        if (!timestamp) return '';
        return new Date(timestamp * 1000).toLocaleString();
    };

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark p-8">
            <div className="max-w-4xl mx-auto text-slate-800 dark:text-white">
                <div className="mb-8 text-center">
                    <h2 className="text-3xl font-bold mb-2">Knowledge Base</h2>
                    <p className="text-slate-500">Semantic search across your conversation history and documents</p>
                </div>

                {/* Search Bar */}
                <div className="relative max-w-2xl mx-auto mb-10 group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <span className="material-icons text-slate-400">search</span>
                    </div>
                    <input
                        className="w-full pl-11 pr-4 py-4 rounded-xl bg-white dark:bg-[#1a2c36] border border-slate-200 dark:border-slate-700 shadow-sm focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all"
                        placeholder="Search memories..."
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSearch()}
                    />
                    <button
                        className="absolute inset-y-2 right-2 px-4 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-sm font-medium transition-colors"
                        onClick={handleSearch}
                    >
                        Search
                    </button>
                </div>

                {/* Results Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {displayItems.length === 0 ? (
                        <div className="col-span-2 text-center py-12">
                            <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
                                <span className="material-icons text-3xl">content_paste_search</span>
                            </div>
                            <h3 className="text-lg font-medium text-slate-900 dark:text-white">{searched ? 'No results found' : 'Knowledge Base Empty'}</h3>
                            <p className="text-slate-500">{searched ? 'Try a different query' : 'Start chatting to build your knowledge base'}</p>
                        </div>
                    ) : (
                        displayItems.map((item, i) => (
                            <div key={item.id || i} className="bg-white dark:bg-[#1a2c36] border border-slate-200 dark:border-slate-700 rounded-xl p-5 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="px-2 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold uppercase rounded tracking-wider">
                                        {item.metadata?.type || 'document'}
                                    </span>
                                    {item.distance !== undefined && item.distance !== null && (
                                        <span className="text-xs text-green-500 font-medium">
                                            Match: {((1 - item.distance) * 100).toFixed(0)}%
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-4 mb-3 leading-relaxed">
                                    {item.text}
                                </p>
                                <div className="text-[10px] text-slate-400 flex items-center gap-1 border-t border-slate-100 dark:border-slate-800 pt-3">
                                    <span className="material-icons text-[12px]">schedule</span>
                                    {formatDate(item.metadata?.timestamp)}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
