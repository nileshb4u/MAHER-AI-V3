import React, { useState } from 'react';
import { apiClient } from '../client';
import { useAuth } from './AuthProvider';
import './AdminLogin.css';

interface AdminLoginProps {
    onLoginSuccess: () => void;
}

export const AdminLogin: React.FC<AdminLoginProps> = ({ onLoginSuccess }) => {
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const result = await login(password);

            if (result.success) {
                onLoginSuccess();
            } else {
                setError(result.error || 'Invalid password');
            }
        } catch (err) {
            setError('Login failed. Please try again.');
            console.error('Login error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="admin-login-container">
            <div className="admin-login-card">
                <div className="admin-login-header">
                    <svg
                        className="admin-icon"
                        width="48"
                        height="48"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                    >
                        <path d="M12 2a5 5 0 1 0 5 5 5 5 0 0 0-5-5z" />
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <path d="M12 12v3" />
                        <path d="M12 18h.01" />
                    </svg>
                    <h2>Admin Login</h2>
                    <p>Enter admin password to access dashboard</p>
                </div>

                <form onSubmit={handleSubmit} className="admin-login-form">
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter admin password"
                            disabled={loading}
                            autoFocus
                            required
                        />
                    </div>

                    {error && (
                        <div className="error-message">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                            </svg>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="login-button"
                        disabled={loading || !password}
                    >
                        {loading ? (
                            <>
                                <span className="spinner"></span>
                                Logging in...
                            </>
                        ) : (
                            'Login'
                        )}
                    </button>
                </form>

                <div className="admin-login-footer">
                    <p>Admin access only • Unauthorized access is prohibited</p>
                </div>
            </div>
        </div>
    );
};
