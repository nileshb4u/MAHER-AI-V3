import React, { useState, useEffect } from 'react';
import { apiClient, AgentData } from '../client';
import { useAuth } from './AuthProvider';
import { AppView } from '../types';

interface AgentStats {
  myTimeSaved: number;
  publishedCount: number;
  timeSavedByMyAgents: number;
}

// Agent Card Component
interface AgentCardProps {
  agent: AgentData;
  onEdit: (id: string) => void;
  onDelete: (id: string, name: string) => void;
  onPublish?: (id: string) => void;
  onUnpublish?: (id: string) => void;
  deleteConfirm: string | null;
  setDeleteConfirm: (id: string | null) => void;
  isPublished?: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onEdit,
  onDelete,
  onPublish,
  onUnpublish,
  deleteConfirm,
  setDeleteConfirm,
  isPublished = false,
}) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="bg-brand-blue/50 border border-brand-light-blue/30 rounded-lg p-4 hover:border-brand-accent-orange/50 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${isPublished
              ? 'bg-green-500/20 text-green-300 border border-green-500/50'
              : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/50'
              }`}>
              {isPublished ? 'Published' : 'Draft'}
            </span>
          </div>
          <p className="text-sm text-brand-gray mb-3 line-clamp-2">{agent.description}</p>
          <div className="flex items-center gap-4 text-xs text-brand-light-gray">
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              {agent.category}
            </span>
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Created {formatDate(agent.createdAt)}
            </span>
            {agent.updatedAt && agent.updatedAt !== agent.createdAt && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Updated {formatDate(agent.updatedAt)}
              </span>
            )}
            {(agent.networkId || agent.department) && (
              <span className="flex items-center gap-1 text-xs border-l border-brand-light-blue pl-2">
                <svg className="w-4 h-4 text-brand-light-gray" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {agent.networkId && <span className="mr-1">{agent.networkId}</span>}
                {agent.department && <span>({agent.department})</span>}
              </span>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 ml-4">
          <button
            onClick={() => onEdit(agent.id)}
            className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg transition-colors"
            title="Edit Agent"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>

          {!isPublished && onPublish && (
            <button
              onClick={() => onPublish(agent.id)}
              className="p-2 text-green-400 hover:bg-green-500/20 rounded-lg transition-colors"
              title="Publish Agent"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </button>
          )}

          {isPublished && onUnpublish && (
            <button
              onClick={() => onUnpublish(agent.id)}
              className="p-2 text-yellow-400 hover:bg-yellow-500/20 rounded-lg transition-colors"
              title="Unpublish Agent"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
            </button>
          )}

          <button
            onClick={() => {
              if (deleteConfirm === agent.id) {
                onDelete(agent.id, agent.name);
              } else {
                setDeleteConfirm(agent.id);
                setTimeout(() => setDeleteConfirm(null), 3000);
              }
            }}
            className={`p-2 rounded-lg transition-colors ${deleteConfirm === agent.id
              ? 'bg-red-500 text-white'
              : 'text-red-400 hover:bg-red-500/20'
              }`}
            title={deleteConfirm === agent.id ? 'Click again to confirm' : 'Delete Agent'}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

interface AboutMeProps {
  onNavigate: (view: AppView) => void;
}

const AboutMe: React.FC<AboutMeProps> = ({ onNavigate }) => {
  const { isAdmin } = useAuth();
  const [draftAgents, setDraftAgents] = useState<AgentData[]>([]);
  const [publishedAgents, setPublishedAgents] = useState<AgentData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<AgentStats>({
    myTimeSaved: 0,
    publishedCount: 0,
    timeSavedByMyAgents: 0,
  });
  const [activeTab, setActiveTab] = useState<'drafts' | 'published'>('drafts');
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  // Load user's agents
  useEffect(() => {
    loadMyAgents();
  }, []);

  const loadMyAgents = async () => {
    try {
      setIsLoading(true);

      // Fetch agents: 
      // - Admins get ALL agents (to see guest drafts)
      // - Guests get their own agents (drafts)
      const viewMode = isAdmin ? 'all' : 'personal';
      const response = await apiClient.getAgents(true, undefined, viewMode);

      // Separate drafts and published
      // Admins see ALL agents (including system). Guests see only their own non-system (or system if they created it? No system is flag).
      const drafts = response.agents.filter((a: AgentData) => (isAdmin || !a.isSystem) && a.status === 'draft');
      const published = response.agents.filter((a: AgentData) => (isAdmin || !a.isSystem) && a.status === 'published');

      setDraftAgents(drafts);
      setPublishedAgents(published);

      // Update stats
      setStats({
        myTimeSaved: 0, // TODO: Calculate based on usage
        publishedCount: published.length,
        timeSavedByMyAgents: 0, // TODO: Calculate based on other users' usage
      });
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (agentId: string) => {
    // Store agent ID in localStorage and navigate to Agent Studio
    localStorage.setItem('editingAgentId', agentId);
    onNavigate(AppView.AgentStudio);
  };

  const handleDelete = async (agentId: string, agentName: string) => {
    if (deleteConfirm !== agentId) {
      setDeleteConfirm(agentId);
      return;
    }

    try {
      await apiClient.deleteAgent(agentId);
      await loadMyAgents();
      setDeleteConfirm(null);
    } catch (error) {
      console.error('Failed to delete agent:', error);
      alert('Failed to delete agent. Please try again.');
    }
  };

  const handleUnpublish = async (agentId: string) => {
    try {
      // Update agent status to draft
      await apiClient.updateAgent(agentId, { status: 'draft' } as any);
      await loadMyAgents();
    } catch (error) {
      console.error('Failed to unpublish agent:', error);
      alert('Failed to unpublish agent. Please try again.');
    }
  };

  const handlePublish = async (agentId: string) => {
    try {
      await apiClient.publishAgent(agentId);
      await loadMyAgents();
    } catch (error) {
      console.error('Failed to publish agent:', error);
      alert('Failed to publish agent. Please try again.');
    }
  };

  const formatTime = (hours: number): string => {
    if (hours === 0) return 'Coming Soon';
    if (hours < 1) return `${Math.round(hours * 60)} mins`;
    return `${hours.toFixed(1)} hrs`;
  };

  return (
    <div className="p-4 md:p-8 text-white">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">About Me</h1>
        <p className="text-lg text-brand-gray mb-8">
          Track your AI assistant usage, manage your custom agents, and see your impact.
        </p>

        {/* Statistics Tiles */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Stat 1: My Time Saved */}
          <div className="bg-brand-light-blue/10 border border-brand-light-blue/20 rounded-xl p-6 hover:border-brand-accent-orange/50 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-brand-light-gray uppercase tracking-wide">My Time Saved</h3>
              <svg className="w-8 h-8 text-brand-accent-orange" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-4xl font-bold text-white mb-2">{formatTime(stats.myTimeSaved)}</p>
            <p className="text-sm text-brand-gray">Time saved using MAHER AI assistants</p>
          </div>

          {/* Stat 2: My Published Agents */}
          <div className="bg-brand-light-blue/10 border border-brand-light-blue/20 rounded-xl p-6 hover:border-brand-accent-orange/50 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-brand-light-gray uppercase tracking-wide">My Published Agents</h3>
              <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-4xl font-bold text-white mb-2">{stats.publishedCount}</p>
            <p className="text-sm text-brand-gray">Custom AI assistants you've created</p>
          </div>

          {/* Stat 3: Time Saved by My Agents */}
          <div className="bg-brand-light-blue/10 border border-brand-light-blue/20 rounded-xl p-6 hover:border-brand-accent-orange/50 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-brand-light-gray uppercase tracking-wide">Impact</h3>
              <svg className="w-8 h-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <p className="text-4xl font-bold text-white mb-2">{formatTime(stats.timeSavedByMyAgents)}</p>
            <p className="text-sm text-brand-gray">Time saved by others using your agents</p>
          </div>
        </div>

        {/* Manage My Agents Section */}
        <div className="bg-brand-light-blue/10 border border-brand-light-blue/20 rounded-xl overflow-hidden">
          <div className="flex border-b border-brand-light-blue/20">
            <button
              onClick={() => setActiveTab('drafts')}
              className={`flex-1 px-6 py-4 text-sm font-semibold transition-colors ${activeTab === 'drafts'
                ? 'bg-brand-light-blue/20 text-white border-b-2 border-brand-accent-orange'
                : 'text-brand-gray hover:text-white hover:bg-brand-light-blue/10'
                }`}
            >
              {isAdmin ? `Review Queue (${draftAgents.length})` : `My Drafts (${draftAgents.length})`}
            </button>
            <button
              onClick={() => setActiveTab('published')}
              className={`flex-1 px-6 py-4 text-sm font-semibold transition-colors ${activeTab === 'published'
                ? 'bg-brand-light-blue/20 text-white border-b-2 border-brand-accent-orange'
                : 'text-brand-gray hover:text-white hover:bg-brand-light-blue/10'
                }`}
            >
              {isAdmin ? `All Published (${publishedAgents.length})` : `My Published (${publishedAgents.length})`}
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand-accent-orange"></div>
                <p className="mt-4 text-brand-gray">Loading your agents...</p>
              </div>
            ) : activeTab === 'drafts' ? (
              draftAgents.length > 0 ? (
                <div className="space-y-4">
                  {draftAgents.map((agent) => (
                    <AgentCard
                      key={agent.id}
                      agent={agent}
                      onEdit={handleEdit}
                      onDelete={handleDelete}
                      onPublish={isAdmin ? handlePublish : undefined}
                      deleteConfirm={deleteConfirm}
                      setDeleteConfirm={setDeleteConfirm}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-brand-gray">
                  <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="text-xl font-semibold text-white mb-2">No Draft Agents</h3>
                  <p className="text-base mb-4">Create a custom agent in Agent Studio and save it as a draft.</p>
                  <button
                    onClick={() => onNavigate(AppView.AgentStudio)}
                    className="px-4 py-2 bg-brand-accent-orange text-white rounded-lg hover:bg-opacity-90 transition-colors"
                  >
                    Go to Agent Studio
                  </button>
                </div>
              )
            ) : (
              publishedAgents.length > 0 ? (
                <div className="space-y-4">
                  {publishedAgents.map((agent) => (
                    <AgentCard
                      key={agent.id}
                      agent={agent}
                      onEdit={handleEdit}
                      onDelete={handleDelete}
                      onUnpublish={isAdmin ? handleUnpublish : undefined}
                      deleteConfirm={deleteConfirm}
                      setDeleteConfirm={setDeleteConfirm}
                      isPublished
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-brand-gray">
                  <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="text-xl font-semibold text-white mb-2">No Published Agents</h3>
                  <p className="text-base mb-4">Publish your agents to make them available to everyone in the Toolroom.</p>
                  <button
                    onClick={() => onNavigate(AppView.AgentStudio)}
                    className="px-4 py-2 bg-brand-accent-orange text-white rounded-lg hover:bg-opacity-90 transition-colors"
                  >
                    Create Agent
                  </button>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutMe;
