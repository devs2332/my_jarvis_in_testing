import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';

export default function Sidebar({ connected, isCollapsed, toggleCollapse, darkMode, setDarkMode, className = '' }) {
    const location = useLocation();

    const navItems = [
        { id: 'chat', icon: 'chat_bubble_outline', label: 'Chat', path: '/' },
        { id: 'history', icon: 'history', label: 'History', path: '/history' },
        { id: 'trash', icon: 'delete_outline', label: 'Trash', path: '/trash' },
        { id: 'settings', icon: 'settings', label: 'Settings', path: '/settings' },
    ];

    const handleDarkModeToggle = () => {
        setDarkMode(!darkMode);
    };

    return (
        <aside className={`${isCollapsed ? 'w-20' : 'w-[280px]'} h-full bg-[#f9fafb] dark:bg-[#15232b] border-r border-gray-200 dark:border-slate-800 flex flex-col shrink-0 transition-all duration-300 relative ${className}`}>
            {/* Header */}
            <div className={`p-5 flex items-center mb-2 ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
                <div className={`flex items-center gap-3 ${isCollapsed ? 'justify-center' : ''}`}>
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white shadow-sm shrink-0">
                        <span className="material-icons text-[18px]">smart_toy</span>
                    </div>
                    {!isCollapsed && <span className="font-bold text-[17px] tracking-tight text-gray-900 dark:text-white">Jarvis</span>}
                </div>
                {!isCollapsed && (
                    <button onClick={toggleCollapse} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                        <span className="material-icons text-xl">left_panel_close</span>
                    </button>
                )}
            </div>

            {/* Collapse Toggle for collapsed state */}
            {isCollapsed && (
                <button
                    onClick={toggleCollapse}
                    className="absolute -right-3 top-6 w-6 h-6 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-full flex items-center justify-center text-slate-500 hover:text-primary transition-colors shadow-sm z-50"
                >
                    <span className="material-icons text-sm">chevron_right</span>
                </button>
            )}

            {/* New Chat Button */}
            <div className="px-5 py-2 mb-2">
                <NavLink
                    to="/"
                    className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-full text-gray-700 dark:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-700 transition shadow-[0_2px_4px_rgba(0,0,0,0.02)] font-medium text-[15px] ${isCollapsed ? 'px-0 rounded-xl' : ''}`}
                    title={isCollapsed ? "New Chat" : ""}
                >
                    <span className="material-icons text-xl">add</span>
                    {!isCollapsed && "New Chat"}
                </NavLink>
            </div>

            {/* Scrollable Navigation List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-6 mt-2">
                <div>
                    {!isCollapsed && <div className="text-[11px] font-bold text-gray-400 dark:text-slate-500 mb-2 px-4 tracking-wider uppercase">Menu</div>}
                    <div className="space-y-0.5">
                        {navItems.map(item => (
                            <NavLink
                                key={item.id}
                                to={item.path}
                                title={isCollapsed ? item.label : ""}
                                className={({ isActive }) => `
                                    flex items-center gap-3 px-4 py-2 rounded-xl transition font-medium
                                    ${isActive
                                        ? 'bg-white dark:bg-slate-800 shadow-[0_1px_3px_rgba(0,0,0,0.05)] dark:shadow-black/20 border border-transparent text-gray-900 dark:text-white'
                                        : 'text-gray-500 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800/60'
                                    }
                                    ${isCollapsed ? 'justify-center px-0' : ''}
                                `}
                            >
                                <span className={`material-icons text-lg ${location.pathname === item.path ? 'text-primary' : 'text-gray-400 dark:text-slate-500'}`}>{item.icon}</span>
                                {!isCollapsed && <span className="truncate text-sm">{item.label}</span>}
                            </NavLink>
                        ))}
                    </div>
                </div>
            </div>

            {/* Dark Mode Toggle */}
            <div className={`px-4 pb-2 ${isCollapsed ? 'flex justify-center' : ''}`}>
                <button
                    onClick={handleDarkModeToggle}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all w-full hover:bg-gray-100 dark:hover:bg-slate-800 ${isCollapsed ? 'justify-center' : ''}`}
                    title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                >
                    <span className={`material-icons text-lg ${darkMode ? 'text-slate-400' : 'text-amber-500'}`}>
                        {darkMode ? 'dark_mode' : 'light_mode'}
                    </span>
                    {!isCollapsed && (
                        <div className="flex-1 flex items-center justify-between">
                            <span className="text-[13px] font-medium text-gray-600 dark:text-slate-300">
                                {darkMode ? 'Dark Mode' : 'Light Mode'}
                            </span>
                            {/* Toggle Switch — ON = dark mode active */}
                            <div className={`relative inline-flex h-5 w-9 rounded-full transition-colors ${darkMode ? 'bg-primary' : 'bg-gray-200 dark:bg-slate-700'}`}>
                                <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform duration-200 ${darkMode ? 'translate-x-4' : 'translate-x-0.5'}`} />
                            </div>
                        </div>
                    )}
                </button>
            </div>

            {/* Status Indicator */}
            <div className={`px-4 pb-3 ${isCollapsed ? 'flex justify-center' : ''}`}>
                <div className={`flex items-center gap-2 px-3 py-2 rounded-xl bg-gray-50 dark:bg-slate-900/50 border border-gray-100 dark:border-slate-800 transition-all ${isCollapsed ? 'justify-center' : ''}`}>
                    <div className="relative flex items-center justify-center w-2.5 h-2.5 shrink-0">
                        <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${connected ? 'bg-green-400' : 'bg-red-400'}`}></span>
                        <span className={`relative inline-flex rounded-full w-2 h-2 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                    </div>
                    {!isCollapsed && (
                        <div className="flex flex-col">
                            <span className="text-[10px] font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wide leading-none mb-0.5">System</span>
                            <span className={`text-[12px] font-medium leading-none ${connected ? 'text-gray-700 dark:text-green-400' : 'text-red-500 dark:text-red-400'}`}>
                                {connected ? 'Operational' : 'Connecting...'}
                            </span>
                        </div>
                    )}
                </div>
            </div>

            {/* User Profile */}
            <NavLink
                to="/profile"
                className={`p-4 border-t border-gray-200 dark:border-slate-800 hover:bg-gray-100 dark:hover:bg-slate-800 transition cursor-pointer flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}
                title={isCollapsed ? "Sarah Connor" : ""}
            >
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-orange-100 overflow-hidden flex items-center justify-center shrink-0">
                        <img src="https://api.dicebear.com/7.x/notionists/svg?seed=Sarah&backgroundColor=ffe0b2" alt="User Profile" className="w-full h-full object-cover" />
                    </div>
                    {!isCollapsed && (
                        <div>
                            <div className="font-bold text-sm text-gray-900 dark:text-white leading-tight">Sarah Connor</div>
                            <div className="text-[13px] text-gray-500 dark:text-slate-400 font-medium">Pro Plan</div>
                        </div>
                    )}
                </div>
                {!isCollapsed && (
                    <button className="text-gray-400 hover:text-gray-700 dark:hover:text-slate-300 shrink-0">
                        <span className="material-icons text-xl">settings</span>
                    </button>
                )}
            </NavLink>
        </aside>
    );
}
