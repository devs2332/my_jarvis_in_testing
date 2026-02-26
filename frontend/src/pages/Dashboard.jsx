import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { fetchJSON } from '../utils/api';
import { Link } from 'react-router-dom';

export default function Dashboard() {
    const { user, loading } = useAuth();
    const [usage, setUsage] = useState({ tokens_used: 0, token_limit: 100000 });
    const [statsLoading, setStatsLoading] = useState(true);

    useEffect(() => {
        // Fetch real usage from backend if available, fallback to user object
        const fetchUsage = async () => {
            try {
                // If there's an endpoint for billing/usage, use it, otherwise use user struct
                const data = await fetchJSON('/api/v1/metrics/usage').catch(() => null);
                if (data) {
                    setUsage(data);
                } else if (user) {
                    setUsage({
                        tokens_used: user.tokens_used || 0,
                        token_limit: user.plan === 'pro' ? 1000000 : (user.plan === 'enterprise' ? 10000000 : 50000)
                    });
                }
            } finally {
                setStatsLoading(false);
            }
        };
        if (user) fetchUsage();
    }, [user]);

    if (loading || statsLoading) return <div className="p-8 text-white">Loading...</div>;

    const percentUsed = Math.min((usage.tokens_used / usage.token_limit) * 100, 100).toFixed(1);

    return (
        <div className="flex-1 overflow-y-auto p-8 bg-[#0b1217] text-white">
            <div className="max-w-4xl mx-auto space-y-8">
                <div>
                    <h1 className="text-3xl font-bold font-display">Overview</h1>
                    <p className="text-gray-400 mt-2">Manage your Jarvis AI Enterprise Platform usage.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Plan Card */}
                    <div className="bg-[#131b22] border border-gray-800 rounded-2xl p-6 shadow-lg">
                        <h2 className="text-lg font-medium text-gray-300 mb-4">Current Plan</h2>
                        <div className="flex items-end gap-3 mb-6">
                            <span className="text-4xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent capitalize">
                                {user?.plan || 'Free'}
                            </span>
                            <span className="text-gray-500 mb-1">tier</span>
                        </div>
                        <p className="text-sm text-gray-400 mb-6">
                            You are currently on the {user?.plan || 'Free'} plan. Upgrade for higher limits, faster processing, and advanced reasoning models like GPT-4o.
                        </p>
                        <Link
                            to="/subscription"
                            className="inline-block px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors text-sm font-medium border border-gray-700"
                        >
                            Manage Subscription
                        </Link>
                    </div>

                    {/* Usage Card */}
                    <div className="bg-[#131b22] border border-gray-800 rounded-2xl p-6 shadow-lg">
                        <h2 className="text-lg font-medium text-gray-300 mb-4">Token Usage</h2>
                        <div className="flex justify-between items-end mb-2">
                            <span className="text-3xl font-bold text-white">{usage.tokens_used.toLocaleString()}</span>
                            <span className="text-sm text-gray-500 mb-1">/ {usage.token_limit.toLocaleString()}</span>
                        </div>

                        <div className="w-full bg-gray-800 rounded-full h-2.5 mb-2 mt-4 overflow-hidden">
                            <div
                                className={`h-2.5 rounded-full ${percentUsed > 90 ? 'bg-red-500' : percentUsed > 75 ? 'bg-yellow-500' : 'bg-blue-500'}`}
                                style={{ width: `${percentUsed}%` }}
                            ></div>
                        </div>
                        <div className="flex justify-between text-xs text-gray-400">
                            <span>{percentUsed}% used this billing cycle</span>
                            <span>Resets in 14 days</span>
                        </div>
                    </div>
                </div>

                {/* Account Details */}
                <div className="bg-[#131b22] border border-gray-800 rounded-2xl p-6 shadow-lg">
                    <h2 className="text-lg font-medium text-gray-300 mb-6">Account Details</h2>
                    <div className="space-y-4">
                        <div className="flex justify-between border-b border-gray-800 pb-4">
                            <span className="text-gray-400">UUID</span>
                            <span className="font-mono text-sm text-gray-300">{user?.id || 'sys-default-001'}</span>
                        </div>
                        <div className="flex justify-between border-b border-gray-800 pb-4">
                            <span className="text-gray-400">Email Address</span>
                            <span className="text-gray-300">{user?.email || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-gray-800 pb-4">
                            <span className="text-gray-400">Role</span>
                            <span className="text-gray-300 capitalize">{user?.role || 'User'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Status</span>
                            <span className="text-emerald-400 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                                Active
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
