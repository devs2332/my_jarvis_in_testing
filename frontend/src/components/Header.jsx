import React from 'react';

export default function Header({ activeView, researchMode, setResearchMode, language, setLanguage }) {
    const titles = {
        chat: 'Chat',
        knowledge: 'Knowledge Base',
        status: 'System Status',
    };

    return (
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#15232b]">
            <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-slate-800 dark:text-white">{titles[activeView] || 'Dashboard'}</h2>
                {activeView === 'chat' && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary uppercase tracking-wide">
                        Beta
                    </span>
                )}
            </div>

            <div className="flex items-center gap-3">
                <button
                    onClick={() => setResearchMode(!researchMode)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${researchMode
                            ? 'bg-purple-100 text-purple-700 border border-purple-200 dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-700'
                            : 'bg-slate-100 text-slate-600 border border-slate-200 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                        }`}
                >
                    <span className="material-icons text-sm">{researchMode ? 'psychology' : 'bolt'}</span>
                    {researchMode ? 'Deep Research' : 'Fast Mode'}
                </button>

                <button
                    onClick={() => setLanguage(language === 'English' ? 'Hindi' : 'English')}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700 transition-colors"
                >
                    <span className="material-icons text-sm">translate</span>
                    {language === 'English' ? 'English' : 'Hindi'}
                </button>

                <div className="h-4 w-px bg-slate-300 dark:bg-slate-700 mx-1"></div>

                <div className="flex items-center gap-2 text-xs font-medium text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/20 px-2 py-1 rounded">
                    <span className="material-icons text-sm">dataset</span>
                    RAG Active
                </div>
            </div>
        </header>
    );
}
