import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';

export default function Sidebar({ connected, isCollapsed, toggleCollapse, className = '' }) {
    const location = useLocation();

    const navItems = [
        { id: 'chat', icon: 'chat_bubble_outline', label: 'Chat', path: '/' },
        { id: 'history', icon: 'history', label: 'History', path: '/history' },
        { id: 'trash', icon: 'delete_outline', label: 'Trash', path: '/trash' },
        { id: 'settings', icon: 'settings', label: 'Settings', path: '/settings' },
    ];

    return (
        <aside className={`${isCollapsed ? 'w-20' : 'w-[260px]'} flex-shrink-0 flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-[#15232b] h-full transition-all duration-300 relative ${className}`}>

            {/* Collapse Toggle */}
            <button
                onClick={toggleCollapse}
                className="absolute -right-3 top-6 w-6 h-6 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full flex items-center justify-center text-slate-500 hover:text-primary transition-colors shadow-sm z-50"
            >
                <span className="material-icons text-sm">{isCollapsed ? 'chevron_right' : 'chevron_left'}</span>
            </button>

            {/* Branding */}
            <div className="p-4">
                <div className={`flex items-center gap-3 px-2 mb-8 ${isCollapsed ? 'justify-center' : ''}`}>
                    <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white shadow-sm flex-shrink-0">
                        <span className="material-icons text-xl">smart_toy</span>
                    </div>
                    {!isCollapsed && (
                        <div className="overflow-hidden whitespace-nowrap">
                            <h1 className="font-bold text-slate-800 dark:text-white leading-tight">Jarvis AI</h1>
                            <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wide">Enterprise</p>
                        </div>
                    )}
                </div>

                {/* New Chat Action */}
                <NavLink
                    to="/"
                    className={`w-full flex items-center gap-3 px-3 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-primary dark:hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md group mb-6 overflow-hidden ${isCollapsed ? 'justify-center' : ''}`}
                    title={isCollapsed ? "New Chat" : ""}
                >
                    <span className="material-icons text-primary text-xl group-hover:scale-110 transition-transform">add</span>
                    {!isCollapsed && <span className="text-sm font-medium text-slate-700 dark:text-slate-200 whitespace-nowrap">New Chat</span>}
                </NavLink>

                {/* Navigation */}
                <div className="space-y-1 overflow-y-auto max-h-[calc(100vh-250px)]">
                    {!isCollapsed && <h3 className="px-3 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">Menu</h3>}
                    {navItems.map(item => (
                        <NavLink
                            key={item.id}
                            to={item.path}
                            title={isCollapsed ? item.label : ""}
                            className={({ isActive }) => `
                                w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium overflow-hidden relative group
                                ${isActive
                                    ? 'bg-gradient-to-r from-primary/10 to-transparent dark:from-primary/20 text-primary dark:text-white border-l-2 border-primary'
                                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200 border-l-2 border-transparent'
                                }
                                ${isCollapsed ? 'justify-center px-0 pl-0 border-l-0' : ''}
                            `}
                        >
                            <span className={`material-icons text-[20px] flex-shrink-0 transition-colors ${location.pathname === item.path ? 'text-primary' : 'group-hover:text-slate-700 dark:group-hover:text-slate-300'}`}>{item.icon}</span>
                            {!isCollapsed && <span className="whitespace-nowrap">{item.label}</span>}
                        </NavLink>
                    ))}
                </div>
            </div>

            {/* Profile Link */}
            <div className={`mt-auto p-4 border-t border-slate-200 dark:border-slate-800 ${isCollapsed ? 'flex justify-center' : ''}`}>
                <NavLink
                    to="/profile"
                    className={({ isActive }) => `flex items-center gap-3 px-2 py-2 rounded-xl transition-all overflow-hidden border border-transparent ${isActive ? 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700' : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:border-slate-200 dark:hover:border-slate-700/50'} ${isCollapsed ? 'justify-center w-full' : ''}`}
                    title={isCollapsed ? "User Account" : ""}
                >
                    <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-500 dark:text-slate-400 flex-shrink-0">
                        <span className="material-icons text-lg">person</span>
                    </div>
                    {!isCollapsed && (
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">User Account</p>
                        </div>
                    )}
                </NavLink>
            </div>

            {/* Status Footer */}
            <div className={`px-4 pb-4 ${isCollapsed ? 'flex justify-center' : ''}`}>
                <div className={`flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800 transition-all hover:bg-white dark:hover:bg-slate-800 hover:shadow-md group cursor-default ${isCollapsed ? 'justify-center' : ''}`}>
                    <div className="relative flex items-center justify-center w-2.5 h-2.5">
                        <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${connected ? 'bg-green-400' : 'bg-red-400'}`}></span>
                        <span className={`relative inline-flex rounded-full w-2 h-2 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                    </div>
                    {!isCollapsed && (
                        <div className="flex flex-col">
                            <span className="text-[11px] font-bold text-slate-700 dark:text-slate-200 leading-none">System Status</span>
                            <span className={`text-[10px] font-medium leading-none mt-0.5 ${connected ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                                {connected ? 'Operational' : 'Disconnected'}
                            </span>
                        </div>
                    )}
                </div>
            </div>
        </aside>
    );
}
