import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchJSON, postJSON } from '../utils/api';
import { decodeJWT } from '../utils/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('jarvis_token');
            if (token) {
                const decoded = decodeJWT(token);
                if (decoded && decoded.exp * 1000 > Date.now()) {
                    try {
                        // Fetch fresh user data using the token
                        const userData = await fetchJSON('/api/v1/auth/me');
                        setUser(userData);
                    } catch (err) {
                        console.error('Failed to validate token', err);
                        localStorage.removeItem('jarvis_token');
                    }
                } else {
                    localStorage.removeItem('jarvis_token');
                }
            }
            setLoading(false);
        };
        initAuth();
    }, []);

    const login = async (email, password) => {
        const res = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!res.ok) {
            const err = await res.json();
            let errorMessage = 'Login failed';
            if (err.detail) {
                if (typeof err.detail === 'string') {
                    errorMessage = err.detail;
                } else if (Array.isArray(err.detail) && err.detail.length > 0) {
                    errorMessage = err.detail[0].msg || JSON.stringify(err.detail[0]);
                } else {
                    errorMessage = JSON.stringify(err.detail);
                }
            }
            throw new Error(errorMessage);
        }

        const data = await res.json();
        const token = data.access_token;
        localStorage.setItem('jarvis_token', token);

        const userData = await fetchJSON('/api/v1/auth/me');
        setUser(userData);
    };

    const register = async (email, password, fullName) => {
        await postJSON('/api/v1/auth/register', {
            email,
            password,
            full_name: fullName
        });
        // Auto-login after registration
        await login(email, password);
    };

    const logout = () => {
        localStorage.removeItem('jarvis_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
