import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { postJSON } from '../utils/api';

export default function Subscription() {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleSubscribe = async (tier) => {
        setLoading(true);
        try {
            // Assume the backend has a Stripe checkout endpoint
            const res = await postJSON('/api/v1/billing/create-checkout-session', { plan: tier });
            if (res.url) {
                window.location.href = res.url;
            } else {
                alert('Billing portal unavailable.');
            }
        } catch (err) {
            console.error('Subscription error:', err);
            alert('Failed to initialize checkout session: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handlePortal = async () => {
        setLoading(true);
        try {
            // Endpoint to manage existing subscription
            const res = await postJSON('/api/v1/billing/portal', {});
            if (res.url) window.location.href = res.url;
        } catch (err) {
            alert('Billing portal error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-1 overflow-y-auto p-8 bg-[#0b1217] text-white">
            <div className="max-w-5xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold font-display mb-4">Upgrade Your Intelligence</h1>
                    <p className="text-gray-400 text-lg">Choose the plan that fits your execution needs.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Free Tier */}
                    <div className="bg-[#131b22] border border-gray-800 rounded-2xl p-8 flex flex-col items-center">
                        <h2 className="text-xl text-gray-300 font-semibold mb-2">Free</h2>
                        <div className="text-4xl font-bold mb-6">$0<span className="text-sm font-normal text-gray-500">/mo</span></div>
                        <ul className="text-sm text-gray-400 space-y-3 mb-8 w-full">
                            <li className="flex gap-2 items-center"><span className="text-emerald-500">✓</span> 50,000 requests/mo</li>
                            <li className="flex gap-2 items-center"><span className="text-emerald-500">✓</span> GPT-4o-mini access</li>
                            <li className="flex gap-2 items-center"><span className="text-emerald-500">✓</span> Standard web search</li>
                            <li className="flex gap-2 items-center"><span className="text-gray-600">✗</span> Advanced browser automation</li>
                        </ul>
                        <button
                            className="mt-auto w-full py-3 px-4 bg-gray-800 text-white rounded-lg cursor-default opacity-50 font-medium"
                            disabled
                        >
                            {user?.plan === 'free' || !user?.plan ? 'Current Plan' : 'Select'}
                        </button>
                    </div>

                    {/* Pro Tier */}
                    <div className="bg-[#131b22] border border-blue-500/50 rounded-2xl p-8 flex flex-col items-center relative transform scale-105 shadow-[0_0_30px_rgba(59,130,246,0.15)] shadow-blue-500/20 z-10">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-xs font-bold px-3 py-1 rounded-full">RECOMMENDED</div>
                        <h2 className="text-xl text-blue-400 font-semibold mb-2">Pro</h2>
                        <div className="text-4xl font-bold mb-6">$20<span className="text-sm font-normal text-gray-500">/mo</span></div>
                        <ul className="text-sm text-gray-400 space-y-3 mb-8 w-full">
                            <li className="flex gap-2 items-center"><span className="text-blue-500">✓</span> 1,000,000 requests/mo</li>
                            <li className="flex gap-2 items-center"><span className="text-blue-500">✓</span> GPT-4o architecture</li>
                            <li className="flex gap-2 items-center"><span className="text-blue-500">✓</span> Deep Research Dorking</li>
                            <li className="flex gap-2 items-center"><span className="text-blue-500">✓</span> Full Web Scraping</li>
                        </ul>
                        {user?.plan === 'pro' ? (
                            <button
                                onClick={handlePortal}
                                disabled={loading}
                                className="mt-auto w-full py-3 px-4 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors font-medium border border-gray-700"
                            >
                                Manage Billing
                            </button>
                        ) : (
                            <button
                                onClick={() => handleSubscribe('pro')}
                                disabled={loading}
                                className="mt-auto w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-lg shadow-lg"
                            >
                                Upgrade to Pro
                            </button>
                        )}
                    </div>

                    {/* Enterprise Tier */}
                    <div className="bg-[#131b22] border border-gray-800 rounded-2xl p-8 flex flex-col items-center">
                        <h2 className="text-xl text-emerald-400 font-semibold mb-2">Enterprise</h2>
                        <div className="text-4xl font-bold mb-6">$99<span className="text-sm font-normal text-gray-500">/mo</span></div>
                        <ul className="text-sm text-gray-400 space-y-3 mb-8 w-full">
                            <li className="flex gap-2 items-center"><span className="text-emerald-500">✓</span> Unlimited standard requests</li>
                            <li className="flex gap-2 items-center"><span className="text-emerald-500">✓</span> Dedicated fine-tuned models</li>
                            <li className="flex gap-2 items-center"><span className="text-emerald-500">✓</span> API Key access</li>
                            <li className="flex gap-2 items-center"><span className="text-emerald-500">✓</span> Priority execution cluster</li>
                        </ul>
                        {user?.plan === 'enterprise' ? (
                            <button
                                onClick={handlePortal}
                                disabled={loading}
                                className="mt-auto w-full py-3 px-4 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors font-medium border border-gray-700"
                            >
                                Manage Billing
                            </button>
                        ) : (
                            <button
                                onClick={() => handleSubscribe('enterprise')}
                                disabled={loading}
                                className="mt-auto w-full py-3 px-4 border border-emerald-500/50 hover:bg-emerald-500/10 text-emerald-400 font-medium rounded-lg transition-colors"
                            >
                                Contact Sales
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
