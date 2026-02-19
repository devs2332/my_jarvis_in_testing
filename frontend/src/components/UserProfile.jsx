import React, { useState } from 'react';

export default function UserProfile() {
    return (
        <div className="flex-1 flex flex-col h-[calc(100vh-theme(spacing.16))] overflow-hidden relative bg-background-light dark:bg-background-dark text-slate-900 dark:text-white font-display">
            <header className="h-16 flex items-center justify-between px-6 lg:px-10 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-background-dark/80 backdrop-blur-sm z-10 shrink-0">
                <div>
                    <h1 className="text-xl font-bold">Account Settings</h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Manage your profile, subscription, and security.</p>
                </div>
                <button className="px-4 py-2 bg-white dark:bg-[#1e2936] border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm">
                    View Public Profile
                </button>
            </header>

            <div className="flex-1 overflow-y-auto p-6 lg:p-10">
                <div className="max-w-5xl mx-auto space-y-8 pb-12">

                    <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                        {/* Profile Information (Span 8) */}
                        <div className="md:col-span-8 bg-white dark:bg-[#15222b] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col">
                            <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800/50 flex justify-between items-center bg-slate-50/50 dark:bg-slate-800/20">
                                <h2 className="text-lg font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                                    <span className="material-icons text-primary text-xl">person</span>
                                    Profile Information
                                </h2>
                                <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-full border border-green-200 dark:border-green-800">Active</span>
                            </div>

                            <div className="p-6 md:p-8 flex-1">
                                <div className="flex flex-col md:flex-row gap-8 items-start">
                                    {/* Avatar */}
                                    <div className="flex flex-col items-center gap-3">
                                        <div className="relative group cursor-pointer">
                                            <div className="h-28 w-28 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center p-1 border-2 border-slate-100 dark:border-slate-700 relative overflow-hidden text-slate-400 dark:text-slate-500">
                                                <span className="material-icons text-5xl">person</span>
                                                <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-full">
                                                    <span className="material-icons text-white">camera_alt</span>
                                                </div>
                                            </div>
                                            <button className="absolute bottom-1 right-1 h-8 w-8 bg-primary text-white rounded-full flex items-center justify-center shadow-lg hover:bg-blue-600 transition-colors border-2 border-white dark:border-[#15222b]">
                                                <span className="material-icons text-sm">edit</span>
                                            </button>
                                        </div>
                                    </div>

                                    {/* Form */}
                                    <div className="flex-1 w-full space-y-5">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                            <div className="space-y-1.5">
                                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">First Name</label>
                                                <input type="text" placeholder="Your First Name" className="w-full rounded-lg border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none" />
                                            </div>
                                            <div className="space-y-1.5">
                                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Last Name</label>
                                                <input type="text" placeholder="Your Last Name" className="w-full rounded-lg border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none" />
                                            </div>
                                        </div>
                                        <div className="space-y-1.5">
                                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Email Address</label>
                                            <div className="relative">
                                                <span className="material-icons absolute left-3 top-2.5 text-slate-400 text-lg">mail_outline</span>
                                                <input type="email" placeholder="you@example.com" className="w-full pl-10 rounded-lg border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none" />
                                            </div>
                                        </div>
                                        <div className="space-y-1.5">
                                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Bio</label>
                                            <textarea rows="3" placeholder="Tell us a little about yourself..." className="w-full rounded-lg border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none resize-none"></textarea>
                                        </div>
                                        <div className="pt-2 flex justify-end">
                                            <button className="px-5 py-2.5 bg-primary hover:bg-blue-600 text-white rounded-lg text-sm font-medium shadow-lg shadow-primary/20 transition-all active:scale-95">
                                                Save Changes
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Subscription (Span 4) */}
                        <div className="md:col-span-4 space-y-6 flex flex-col">
                            <div className="bg-white dark:bg-[#15222b] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden h-full">
                                <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800/50 bg-gradient-to-r from-slate-50 to-white dark:from-slate-800/30 dark:to-[#15222b]">
                                    <h2 className="text-lg font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                                        <span className="material-icons text-primary text-xl">stars</span>
                                        Subscription
                                    </h2>
                                </div>
                                <div className="p-6 space-y-6">
                                    <div className="bg-primary/5 dark:bg-primary/10 rounded-xl p-5 border border-primary/10 flex items-center justify-between">
                                        <div>
                                            <p className="text-xs uppercase tracking-wide font-bold text-primary mb-1">Current Plan</p>
                                            <h3 className="text-2xl font-bold text-slate-900 dark:text-white">Free Tier</h3>
                                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Upgrade for more power</p>
                                        </div>
                                        <div className="h-12 w-12 bg-white dark:bg-slate-800 rounded-full flex items-center justify-center shadow-sm text-primary">
                                            <span className="material-icons text-2xl">rocket_launch</span>
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="text-slate-500 dark:text-slate-400">Status</span>
                                            <span className="font-medium text-green-600 dark:text-green-400 flex items-center gap-1">
                                                <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> Active
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="text-slate-500 dark:text-slate-400">Next Billing</span>
                                            <span className="font-medium text-slate-900 dark:text-white">--</span>
                                        </div>
                                    </div>
                                    <div className="pt-2">
                                        <button className="w-full py-2.5 border border-primary text-primary hover:bg-primary hover:text-white dark:hover:text-white rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 group">
                                            Upgrade Plan
                                            <span className="material-icons text-sm group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Security Card (Full Width) */}
                        <div className="md:col-span-12 bg-white dark:bg-[#15222b] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                            <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800/50 bg-slate-50/50 dark:bg-slate-800/20">
                                <h2 className="text-lg font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                                    <span className="material-icons text-primary text-xl">security</span>
                                    Security
                                </h2>
                            </div>
                            <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
                                <div className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                                    <div>
                                        <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Password</h3>
                                        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Last changed recently. We recommend rotating it every 6 months.</p>
                                    </div>
                                    <button className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors whitespace-nowrap">
                                        Change Password
                                    </button>
                                </div>
                                <div className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Two-Factor Authentication</h3>
                                            <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-[10px] font-bold uppercase rounded-sm tracking-wider">Disabled</span>
                                        </div>
                                        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Add an extra layer of security to your account.</p>
                                    </div>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input className="sr-only peer" type="checkbox" />
                                        <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 dark:peer-focus:ring-primary/30 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-primary"></div>
                                    </label>
                                </div>
                            </div>
                        </div>

                        {/* Danger Zone */}
                        <div className="md:col-span-12 mt-4 pt-6 border-t border-slate-200 dark:border-slate-800/50">
                            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                                <div>
                                    <h3 className="text-sm font-semibold text-red-600 dark:text-red-400">Delete Account</h3>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-xl">Permanently remove your Personal Account and all of its contents from the platform. This action is not reversible.</p>
                                </div>
                                <button className="px-4 py-2 bg-white dark:bg-[#15222b] border border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 rounded-lg text-sm font-medium hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors">
                                    Delete Account
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
