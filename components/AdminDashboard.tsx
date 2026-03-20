import React, { useEffect, useState } from 'react';
import { apiClient } from '../client';
import './AdminDashboard.css';

interface AnalyticsData {
    total_visits: number;
    total_chats: number;
    total_agents: number;
    active_users: number;
    visits_today: number;
    chats_today: number;
    top_agents: Array<{ agent: string; count: number }>;
    recent_activity: Array<{
        id: number;
        agent: string;
        messages: number;
        time: string;
    }>;
}

export const AdminDashboard: React.FC = () => {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadAnalytics();
        // Refresh every 30 seconds
        const interval = setInterval(loadAnalytics, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadAnalytics = async () => {
        try {
            const data = await apiClient.getAnalytics();
            setAnalytics(data);
            setError('');
        } catch (err) {
            setError('Failed to load analytics');
            console.error('Analytics error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = async () => {
        try {
            await apiClient.logout();
            window.location.href = '/';
        } catch (err) {
            console.error('Logout error:', err);
            // Force reload anyway
            window.location.href = '/';
        }
    };

    if (loading) {
        return (
            <div className="admin-dashboard-loading">
                <div className="spinner-large"></div>
                <p>Loading dashboard...</p>
            </div>
        );
    }

    if (error || !analytics) {
        return (
            <div className="admin-dashboard-error">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                </svg>
                <h2>Error Loading Dashboard</h2>
                <p>{error}</p>
                <button onClick={loadAnalytics} className="retry-button">
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="admin-dashboard">
            <div className="dashboard-header">
                <div>
                    <h1>Admin Dashboard</h1>
                    <p>Real-time analytics and system overview</p>
                </div>
                <button onClick={handleLogout} className="logout-button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                        <polyline points="16 17 21 12 16 7" />
                        <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                    Logout
                </button>
            </div>

            <div className="kpi-grid">
                <div className="kpi-card">
                    <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                            <circle cx="9" cy="7" r="4" />
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                        </svg>
                    </div>
                    <div className="kpi-content">
                        <div className="kpi-label">Total Visits</div>
                        <div className="kpi-value">{analytics.total_visits.toLocaleString()}</div>
                        <div className="kpi-sublabel">Today: {analytics.visits_today}</div>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                        </svg>
                    </div>
                    <div className="kpi-content">
                        <div className="kpi-label">Total Chats</div>
                        <div className="kpi-value">{analytics.total_chats.toLocaleString()}</div>
                        <div className="kpi-sublabel">Today: {analytics.chats_today}</div>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M12 6v6l4 2" />
                        </svg>
                    </div>
                    <div className="kpi-content">
                        <div className="kpi-label">Active Users</div>
                        <div className="kpi-value">{analytics.active_users.toLocaleString()}</div>
                        <div className="kpi-sublabel">Last 24 hours</div>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5z" />
                            <path d="M2 17l10 5 10-5" />
                            <path d="M2 12l10 5 10-5" />
                        </svg>
                    </div>
                    <div className="kpi-content">
                        <div className="kpi-label">Total Agents</div>
                        <div className="kpi-value">{analytics.total_agents.toLocaleString()}</div>
                        <div className="kpi-sublabel">All agents</div>
                    </div>
                </div>
            </div>

            <div className="dashboard-content">
                <div className="dashboard-section">
                    <h2>Top Agents</h2>
                    <div className="top-agents-list">
                        {analytics.top_agents.length > 0 ? (
                            analytics.top_agents.map((agent, index) => (
                                <div key={index} className="top-agent-item">
                                    <div className="agent-rank">#{index + 1}</div>
                                    <div className="agent-info">
                                        <div className="agent-name">{agent.agent}</div>
                                        <div className="agent-usage">{agent.count} uses</div>
                                    </div>
                                    <div className="agent-bar">
                                        <div
                                            className="agent-bar-fill"
                                            style={{
                                                width: `${(agent.count / analytics.top_agents[0].count) * 100}%`,
                                            }}
                                        ></div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="empty-state">No agent usage data yet</div>
                        )}
                    </div>
                </div>

                <div className="dashboard-section">
                    <h2>Recent Activity</h2>
                    <div className="activity-list">
                        {analytics.recent_activity.length > 0 ? (
                            analytics.recent_activity.map((activity) => (
                                <div key={activity.id} className="activity-item">
                                    <div className="activity-icon">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                            <circle cx="12" cy="12" r="10" />
                                        </svg>
                                    </div>
                                    <div className="activity-content">
                                        <div className="activity-agent">{activity.agent}</div>
                                        <div className="activity-meta">
                                            {activity.messages} message{activity.messages !== 1 ? 's' : ''} •{' '}
                                            {new Date(activity.time).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="empty-state">No recent activity</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
