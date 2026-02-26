import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(email, password);
            navigate('/');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen items-center justify-center bg-[#0b1217] text-white">
            <div className="w-full max-w-md p-8 bg-[#131b22] border border-gray-800 rounded-2xl shadow-2xl">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">Jarvis AI</h1>
                    <p className="text-gray-400 mt-2">Welcome back to the Enterprise Platform</p>
                </div>

                {error && <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-3 bg-[#0b1217] border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder-gray-600"
                            placeholder="agent@cyber.local"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">Password</label>
                        <input
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-3 bg-[#0b1217] border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder-gray-600"
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-medium rounded-lg shadow-lg hover:shadow-blue-500/25 transition-all disabled:opacity-50"
                    >
                        {loading ? 'Authenticating...' : 'Sign In'}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-400">
                    Don't have an account? <Link to="/register" className="text-blue-400 hover:text-blue-300 transition-colors">Request Access</Link>
                </p>
            </div>
        </div>
    );
}
