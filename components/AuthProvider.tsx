import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient } from '../client';
import { SharekUser, authenticateUser } from '../sharekAuth';

interface AuthContextType {
    role: 'guest' | 'admin' | null;
    isAdmin: boolean;
    isGuest: boolean;
    sharekUser: SharekUser | null;
    login: (password: string) => Promise<{ success: boolean; error?: string }>;
    logout: () => Promise<void>;
    refreshRole: () => void;
    initialized: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [role, setRole] = useState<'guest' | 'admin' | null>(null);
    const [sharekUser, setSharekUser] = useState<SharekUser | null>(null);
    const [initialized, setInitialized] = useState(false);

    useEffect(() => {
        initializeSession();
    }, []);

    const initializeSession = async () => {
        try {
            // Attempt Sharek authentication
            // Fallback to window.location.origin if VITE_SHAREK_BASE_URL is not provided
            const sharekBaseUrl = (import.meta as any).env.VITE_SHAREK_BASE_URL || window.location.origin;
            const sUser = await authenticateUser(sharekBaseUrl);
            if (sUser) {
                setSharekUser(sUser);
            }
        } catch (e) {
            console.error("Sharek auth attempt failed:", e);
        }

        try {
            // Check if session exists
            const sessionId = localStorage.getItem('maher_session_id');

            if (sessionId) {
                // Verify existing session
                const result = await apiClient.verifySession();
                if (result.valid && result.role) {
                    setRole(result.role as 'guest' | 'admin');
                } else {
                    // Session invalid, create new guest session
                    const guestSession = await apiClient.createGuestSession();
                    setRole('guest');
                }
            } else {
                // No session, create guest session
                const guestSession = await apiClient.createGuestSession();
                setRole('guest');
            }
        } catch (error) {
            console.error('Session initialization error:', error);
            // Try to create guest session anyway if backend is reachable
            try {
                const guestSession = await apiClient.createGuestSession();
                setRole('guest');
            } catch (err) {
                console.error('Failed to create guest session:', err);
                // Fallback to guest if offline, though functionality will be limited
                setRole('guest');
            }
        } finally {
            setInitialized(true);
        }
    };

    const login = async (password: string) => {
        try {
            const result = await apiClient.adminLogin(password);
            if (result.success) {
                setRole('admin');
                return { success: true };
            }
            return { success: false, error: result.error };
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Login failed' };
        }
    };

    const logout = async () => {
        try {
            await apiClient.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Always revert to guest logic or clear role
            // Usually we want to create a guest session immediately
            try {
                await apiClient.createGuestSession();
                setRole('guest');
            } catch (e) {
                setRole('guest');
            }
        }
    };

    const refreshRole = () => {
        setRole(apiClient.getUserRole());
    };

    if (!initialized) {
        // Show a simple loading spinner while initializing session
        return (
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '100vh',
                background: '#f7fafc'
            }}>
                <div style={{
                    width: '48px',
                    height: '48px',
                    border: '4px solid #e2e8f0',
                    borderTopColor: '#667eea',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                }}>
                    <style>{`
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    `}</style>
                </div>
            </div>
        );
    }

    return (
        <AuthContext.Provider value={{
            role,
            isAdmin: role === 'admin',
            isGuest: role === 'guest',
            sharekUser,
            login,
            logout,
            refreshRole,
            initialized
        }}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook to use auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
