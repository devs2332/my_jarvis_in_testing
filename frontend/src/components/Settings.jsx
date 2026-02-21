import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function Settings({ darkMode, setDarkMode }) {
    const [contextWindow, setContextWindow] = useState(60);
    const [language, setLanguage] = useState('English');
    const [defaultModel, setDefaultModel] = useState('GPT-4');
    const [apiKey, setApiKey] = useState('sk-........................');

    // Toggle states
    const [dataSharing, setDataSharing] = useState(false);
    const [locationAccess, setLocationAccess] = useState(true);
    const [autoSave, setAutoSave] = useState(true);
    const [desktopNotif, setDesktopNotif] = useState(false);
    const [soundEffects, setSoundEffects] = useState(true);
    const [streamResponse, setStreamResponse] = useState(true);

    // No local dark mode state — controlled by global App.jsx via props
    return (
        <div className="flex-1 flex flex-col h-[calc(100vh-theme(spacing.16))] overflow-hidden relative bg-white dark:bg-[#0b1217] text-slate-900 dark:text-white font-display">
            {/* Header */}
            <header className="h-16 flex items-center justify-between px-6 lg:px-10 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#0b1217]/90 backdrop-blur-md z-10 shrink-0 sticky top-0">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-slate-500">
                        <span className="material-icons text-xl">settings</span>
                    </div>
                    <h1 className="text-xl font-bold">Settings</h1>
                </div>
                <button className="px-4 py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors shadow-sm">
                    Save Changes
                </button>
            </header>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-6 lg:p-10 scroll-smooth">
                <div className="max-w-3xl mx-auto space-y-10 pb-20">

                    {/* Account Section */}
                    <section>
                        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 px-1">Account & API</h2>
                        <div className="bg-white dark:bg-[#151b26] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                            <div className="p-6 border-b border-slate-100 dark:border-slate-800/50 flex items-center gap-4">
                                <div className="w-16 h-16 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
                                    <img
                                        src="https://lh3.googleusercontent.com/aida-public/AB6AXuCqRqqcpF_2iSceqvg4CJ0wW7Od-LlROf2ANRSigFwubhzy4oSsQBQ5c6OkPVVG7iSUM_bz2XQSVsq6zu8dVl-4DmBuVoSPc1hRZgXlkJYWzJ7KsXOx7jt_kD5Gew_srYKeQr5OfE0iYY05ch5cd6WESIEQ0pNgNMDGXnyNyr-t9s_GF5JxdaOxMtkAulW-wlyjwGGEIYkQDmmwOPf2Igf0muNfaPUWQIG-B6AXxYbirUB8QVhshnmBFMeDH1orkgr2k0IdafvP3QY"
                                        alt="Profile"
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-bold text-lg">Admin User</h3>
                                    <p className="text-slate-500 text-sm">admin@jarvis.ai</p>
                                </div>
                                <button className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                                    Edit Profile
                                </button>
                            </div>
                            <div className="p-6">
                                <label className="block text-sm font-medium mb-2">OpenAI API Key</label>
                                <div className="flex gap-2">
                                    <input
                                        type="password"
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        className="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono"
                                    />
                                    <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-lg text-sm font-medium hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
                                        Update
                                    </button>
                                </div>
                                <p className="text-xs text-slate-400 mt-2">Your key is stored locally and never shared.</p>
                            </div>
                        </div>
                    </section>

                    {/* App Appearance */}
                    <section>
                        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 px-1">Interface</h2>
                        <div className="bg-white dark:bg-[#151b26] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden divide-y divide-slate-100 dark:divide-slate-800/50">
                            <ToggleItem
                                title="Dark Mode"
                                description="Easy on the eyes, perfect for night time."
                                icon="dark_mode"
                                iconColor="text-indigo-500 bg-indigo-500/10"
                                checked={darkMode}
                                onChange={setDarkMode}
                            />
                            <div className="p-5 flex items-center justify-between group hover:bg-slate-50 dark:hover:bg-[#1a232e] transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
                                        <span className="material-icons text-xl">language</span>
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-bold">Language</h3>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">System language</p>
                                    </div>
                                </div>
                                <select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                    className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-primary cursor-pointer"
                                >
                                    <option>English</option>
                                    <option>Spanish</option>
                                    <option>French</option>
                                </select>
                            </div>
                        </div>
                    </section>

                    {/* Model Configuration */}
                    <section>
                        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 px-1">Intelligence</h2>
                        <div className="bg-white dark:bg-[#151b26] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden divide-y divide-slate-100 dark:divide-slate-800/50">
                            <div className="p-5 flex items-center justify-between group hover:bg-slate-50 dark:hover:bg-[#1a232e] transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                                        <span className="material-icons text-xl">psychology</span>
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-bold">Default Model</h3>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Primary AI engine</p>
                                    </div>
                                </div>
                                <select
                                    value={defaultModel}
                                    onChange={(e) => setDefaultModel(e.target.value)}
                                    className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-primary cursor-pointer"
                                >
                                    <option>GPT-4</option>
                                    <option>GPT-3.5</option>
                                    <option>Claude 2</option>
                                </select>
                            </div>

                            <div className="p-5 group hover:bg-slate-50 dark:hover:bg-[#1a232e] transition-colors">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-4">
                                        <div className="p-2 rounded-lg bg-orange-500/10 text-orange-500">
                                            <span className="material-icons text-xl">memory</span>
                                        </div>
                                        <div>
                                            <h3 className="text-sm font-bold">Context Window</h3>
                                            <p className="text-sm text-slate-500 dark:text-slate-400">Memory depth ({Math.round(4096 * (contextWindow / 100))} tokens)</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="w-full relative h-2 bg-slate-200 dark:bg-slate-700 rounded-full mt-2">
                                    <div className="absolute h-full bg-primary rounded-full" style={{ width: `${contextWindow}%` }}></div>
                                    <input
                                        type="range"
                                        min="1"
                                        max="100"
                                        value={contextWindow}
                                        onChange={(e) => setContextWindow(Number(e.target.value))}
                                        className="absolute w-full h-full opacity-0 cursor-pointer z-10"
                                    />
                                    <div className="absolute w-4 h-4 bg-white border-2 border-primary rounded-full top-1/2 transform -translate-y-1/2 shadow-md pointer-events-none" style={{ left: `${contextWindow}%` }}></div>
                                </div>
                            </div>

                            <ToggleItem
                                title="Stream Responses"
                                description="Typewriter effect for messages."
                                icon="stream"
                                iconColor="text-cyan-500 bg-cyan-500/10"
                                checked={streamResponse}
                                onChange={setStreamResponse}
                            />
                        </div>
                    </section>

                    {/* System & Privacy */}
                    <section>
                        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 px-1">System & Privacy</h2>
                        <div className="bg-white dark:bg-[#151b26] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden divide-y divide-slate-100 dark:divide-slate-800/50">
                            <ToggleItem
                                title="Notifications"
                                description="Desktop alerts for tasks."
                                icon="notifications"
                                iconColor="text-pink-500 bg-pink-500/10"
                                checked={desktopNotif}
                                onChange={setDesktopNotif}
                            />
                            <ToggleItem
                                title="Sound Effects"
                                description="System sounds for interactions."
                                icon="volume_up"
                                iconColor="text-purple-500 bg-purple-500/10"
                                checked={soundEffects}
                                onChange={setSoundEffects}
                            />
                            <ToggleItem
                                title="Data Sharing"
                                description="Help improve models (Anonymized)."
                                icon="share"
                                iconColor="text-blue-500 bg-blue-500/10"
                                checked={dataSharing}
                                onChange={setDataSharing}
                            />
                        </div>
                    </section>

                    {/* Danger Zone */}
                    <section>
                        <h2 className="text-sm font-bold text-red-400 uppercase tracking-wider mb-4 px-1">Danger Zone</h2>
                        <div className="bg-red-50 dark:bg-red-900/5 rounded-2xl border border-red-100 dark:border-red-900/20 p-6 flex items-center justify-between">
                            <div>
                                <h3 className="text-sm font-bold text-red-600 dark:text-red-400">Reset Application</h3>
                                <p className="text-sm text-red-600/70 dark:text-red-400/70 mt-1">Clear all local data and configurations.</p>
                            </div>
                            <button
                                onClick={() => window.confirm("Factory reset? All data will be lost.") && alert("Resetting...")}
                                className="px-4 py-2 bg-white dark:bg-transparent border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm font-medium rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                            >
                                Factory Reset
                            </button>
                        </div>
                    </section>

                </div>
            </div>
        </div>
    );
}

function ToggleItem({ title, description, icon, iconColor, checked, onChange }) {
    return (
        <div className="p-5 flex items-center justify-between group hover:bg-slate-50 dark:hover:bg-[#1a232e] transition-colors cursor-pointer" onClick={() => onChange(!checked)}>
            <div className="flex items-center gap-4">
                {icon && (
                    <div className={`p-2 rounded-lg ${iconColor || 'text-slate-500 bg-slate-100'}`}>
                        <span className="material-icons text-xl">{icon}</span>
                    </div>
                )}
                <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">{title}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{description}</p>
                </div>
            </div>
            <button
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${checked ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
            >
                <span className="sr-only">Use setting</span>
                <span
                    aria-hidden="true"
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${checked ? 'translate-x-5' : 'translate-x-0'}`}
                />
            </button>
        </div>
    );
}
