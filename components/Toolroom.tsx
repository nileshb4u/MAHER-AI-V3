import React, { useState, useMemo, useEffect } from 'react';
import { Agent } from '../types';
import SolutionCard from './SolutionCard';
import AgentModal from './AgentModal';
import { apiClient, AgentData } from '../client';

const Toolroom: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [skillsOnly, setSkillsOnly] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load agents from database on mount
  useEffect(() => {
    const loadAgents = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch only published agents (system + user-published)
        const response = await apiClient.getAgents(false);

        // Convert AgentData to Agent format
        const agentsData: Agent[] = response.agents.map((agentData: AgentData) => ({
          id: agentData.id,
          name: agentData.name,
          description: agentData.description,
          systemPrompt: agentData.systemPrompt,
          category: agentData.category,
          iconSVG: agentData.iconSVG || '',
          iconBackgroundColor: agentData.iconBackgroundColor || '#4f46e5',
          defaultProvider: agentData.defaultProvider,
          displayProviderName: agentData.displayProviderName,
          statusText: agentData.statusText,
          statusClass: agentData.statusClass,
          toolSchema: agentData.toolSchema || null,
          implementationType: agentData.implementationType || 'llm_agent',
          skillVersion: agentData.skillVersion || '1.0.0',
          isSkill: agentData.isSkill || false,
        }));

        setAgents(agentsData);
      } catch (err: any) {
        console.error('Failed to load agents:', err);
        setError('Failed to load AI assistants. Please refresh the page.');
      } finally {
        setIsLoading(false);
      }
    };

    loadAgents();
  }, []);

  const filteredAgents = useMemo(() => {
    return agents.filter(agent => {
      const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = categoryFilter === '' || agent.category === categoryFilter;
      const matchesSkillFilter = !skillsOnly || agent.isSkill;
      return matchesSearch && matchesCategory && matchesSkillFilter;
    });
  }, [agents, searchTerm, categoryFilter, skillsOnly]);

  const handleLaunchAgent = (agent: Agent) => {
    setSelectedAgent(agent);
  };

  const handleCloseModal = () => {
    setSelectedAgent(null);
  };

  return (
    <>
      <div className="w-full text-white">
        {/* Filters Section */}
        <section className="p-4 md:p-8">
          <div className="max-w-6xl mx-auto bg-brand-light-blue/10 p-6 rounded-2xl border border-brand-light-blue/20">
            <h3 className="text-center text-xl font-bold mb-4 text-white">Meet AI Assistant designed by Maintenance Subject Matter Experts</h3>
            <div className="flex flex-col md:flex-row gap-4 justify-center items-center">
              <input
                type="text"
                id="searchSolutions"
                placeholder="Search assistants..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full md:w-1/3 p-3 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white placeholder-brand-gray focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
              />
              <select
                id="filterCategory"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full md:w-1/3 p-3 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
              >
                <option value="">All Categories</option>
                <option value="maintenance">Maintenance & Reliability</option>
                <option value="operations">Operations Support</option>
                <option value="contracts">Contract & Commercial</option>
                <option value="safety">Safety & Compliance</option>
                <option value="projects">Project Management</option>
              </select>
              <button
                onClick={() => setSkillsOnly(!skillsOnly)}
                className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-semibold transition-colors whitespace-nowrap ${
                  skillsOnly
                    ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
                    : 'bg-brand-blue border-brand-light-blue/30 text-brand-gray hover:border-purple-500/40 hover:text-purple-300'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Skills Only
              </button>
            </div>
          </div>
        </section>

        {/* Solutions Grid */}
        <section className="p-4 md:p-8">
          <div className="max-w-6xl mx-auto">
            {isLoading ? (
              <div className="text-center py-16">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent-orange"></div>
                <p className="mt-4 text-brand-gray">Loading AI assistants...</p>
              </div>
            ) : error ? (
              <div className="text-center py-16 text-red-400">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <h3 className="mt-2 text-xl font-semibold text-white">Error Loading Assistants</h3>
                <p className="mt-1 text-base">{error}</p>
                <button
                  onClick={() => window.location.reload()}
                  className="mt-4 px-4 py-2 bg-brand-accent-orange text-white rounded-lg hover:bg-opacity-90 transition-colors"
                >
                  Reload Page
                </button>
              </div>
            ) : filteredAgents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredAgents.map(agent => (
                  <SolutionCard key={agent.id} agent={agent} onLaunch={handleLaunchAgent} />
                ))}
              </div>
            ) : (
              <div className="text-center py-16 text-brand-gray">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                <h3 className="mt-2 text-xl font-semibold text-white">No AI Assistants Found</h3>
                <p className="mt-1 text-base">Try adjusting your search or filter criteria.</p>
              </div>
            )}
          </div>
        </section>
      </div>
      {selectedAgent && (
        <AgentModal agent={selectedAgent} onClose={handleCloseModal} />
      )}
    </>
  );
};

export default Toolroom;