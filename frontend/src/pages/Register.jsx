import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
    const { register } = useAuth();
    const navigate = useNavigate();
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register(email, password, fullName);
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
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">Join Jarvis</h1>
                    <p className="text-gray-400 mt-2">Create an enterprise account</p>
                </div>

                {error && <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">Full Name</label>
                        <input
                            type="text"
                            required
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            className="w-full px-4 py-3 bg-[#0b1217] border border-gray-700 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition-all placeholder-gray-600"
                            placeholder="John Doe"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-3 bg-[#0b1217] border border-gray-700 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition-all placeholder-gray-600"
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
                            className="w-full px-4 py-3 bg-[#0b1217] border border-gray-700 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition-all placeholder-gray-600"
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium rounded-lg shadow-lg hover:shadow-emerald-500/25 transition-all disabled:opacity-50 mt-2"
                    >
                        {loading ? 'Creating Account...' : 'Register'}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-400">
                    Already have an account? <Link to="/login" className="text-emerald-400 hover:text-emerald-300 transition-colors">Sign In</Link>
                </p>
            </div>
        </div>
    );
}
