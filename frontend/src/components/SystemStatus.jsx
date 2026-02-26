import React, { useState, useEffect } from 'react';
import { fetchJSON } from '../utils/api';

export default function SystemStatus() {
    const [status, setStatus] = useState(null);
    const [facts, setFacts] = useState({});

    useEffect(() => {
        fetchJSON('/api/v1/status').then(setStatus).catch(() => { });
        fetchJSON('/api/v1/facts').then(data => setFacts(data.facts || {})).catch(() => { });
    }, []);

    if (!status) {
        return (
            <div className="flex-1 flex items-center justify-center h-full bg-background-light dark:bg-background-dark">
                <div className="text-center">
                    <span className="material-icons text-4xl text-slate-300 animate-spin">refresh</span>
                    <p className="mt-2 text-slate-500">Connecting to system...</p>
                </div>
            </div>
        );
    }

    const StatCard = ({ icon, color, title, value, sub, children }) => (
        <div className="bg-white dark:bg-[#1a2c36] border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm hover:shadow-md transition-all">
            <div className="flex items-start justify-between mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white ${color}`}>
                    <span className="material-icons">{icon}</span>
                </div>
                <div className="text-right">
                    <div className="text-2xl font-bold text-slate-800 dark:text-white">{value}</div>
                    <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">{title}</div>
                </div>
            </div>
            {sub && <div className="text-sm text-slate-500 dark:text-slate-400 mb-2">{sub}</div>}
            {children}
        </div>
    );

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark p-8">
            <div className="max-w-6xl mx-auto">
                <h2 className="text-3xl font-bold mb-8 text-slate-800 dark:text-white">System Status</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <StatCard
                        icon="smart_toy"
                        color="bg-blue-500"
                        title="LLM Provider"
                        value={status.llm_provider?.toUpperCase()}
                        sub="Active AI Model"
                    />

                    <StatCard
                        icon="storage"
                        color="bg-purple-500"
                        title="Vector Memory"
                        value={status.vector_memory?.total_documents ?? 0}
                        sub="Documents in ChromaDB"
                    />

                    <StatCard
                        icon="api"
                        color="bg-cyan-500"
                        title="API Server"
                        value="ONLINE"
                        sub="FastAPI v2.0.0"
                    >
                        <div className="mt-2 flex items-center gap-1 text-xs text-green-500 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                            Operational
                        </div>
                    </StatCard>

                    <StatCard
                        icon="extension"
                        color="bg-green-500"
                        title="Tools"
                        value={status.tools_count}
                        sub="Registered Extensions"
                    >
                        <div className="flex flex-wrap gap-1 mt-2">
                            {status.tools?.slice(0, 6).map(tool => (
                                <span key={tool} className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-[10px] rounded">
                                    {tool}
                                </span>
                            ))}
                            {status.tools?.length > 6 && <span className="text-[10px] text-slate-400">+ more</span>}
                        </div>
                    </StatCard>

                    <StatCard
                        icon="memory"
                        color="bg-orange-500"
                        title="Facts"
                        value={Object.keys(facts).length}
                        sub="Key-Value Memories"
                    >
                        <div className="space-y-1 mt-2">
                            {Object.entries(facts).slice(0, 3).map(([k, v]) => (
                                <div key={k} className="flex justify-between text-xs border-b border-slate-100 dark:border-slate-700 pb-1 last:border-0">
                                    <span className="font-medium text-slate-600 dark:text-slate-300">{k}</span>
                                    <span className="text-slate-400 truncate max-w-[100px]">{typeof v === 'string' ? v : JSON.stringify(v)}</span>
                                </div>
                            ))}
                        </div>
                    </StatCard>

                    <StatCard
                        icon="architecture"
                        color="bg-indigo-500"
                        title="Architecture"
                        value="RAG"
                        sub="Retrieval Augmented Gen"
                    />
                </div>
            </div>
        </div>
    );
}
