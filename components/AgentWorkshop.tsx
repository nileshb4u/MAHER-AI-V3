
import React, { useState } from 'react';
import { Agent } from '../types';
import AgentBuilderChat from './AgentBuilderChat';

const AgentWorkshop: React.FC = () => {
  const [agentConfig, setAgentConfig] = useState<Partial<Agent>>({
    name: 'New Maintenance Agent',
    systemPrompt: 'You are a helpful assistant for industrial maintenance tasks. You are an expert in reading and interpreting technical manuals and schematics. When a user asks a question, first determine the equipment they are asking about. Then, provide clear, step-by-step instructions. Always prioritize safety warnings and list required tools before the procedure.',
    description: 'An agent designed to help with maintenance procedures.',
    category: 'maintenance',
  });

  return (
    <div className="flex flex-col md:flex-row h-full text-white bg-brand-deep-blue">
      {/* Configuration Panel */}
      <div className="w-full md:w-1/2 lg:w-1/3 p-6 border-r border-brand-light-blue/20 overflow-y-auto">
        <h2 className="text-2xl font-bold mb-2">Agent Workshop</h2>
        <p className="text-sm text-brand-gray mb-6">
          Define the core identity, instructions, and capabilities for your custom AI agent.
        </p>
        
        <form className="space-y-4">
          <div>
            <label htmlFor="agentName" className="block text-sm font-medium text-brand-light-gray mb-1">Agent Name</label>
            <input
              type="text"
              id="agentName"
              value={agentConfig.name || ''}
              onChange={(e) => setAgentConfig({ ...agentConfig, name: e.target.value })}
              className="w-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
            />
          </div>
          <div>
            <label htmlFor="agentDescription" className="block text-sm font-medium text-brand-light-gray mb-1">Description</label>
            <textarea
              id="agentDescription"
              rows={3}
              value={agentConfig.description || ''}
              onChange={(e) => setAgentConfig({ ...agentConfig, description: e.target.value })}
              className="w-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white resize-none focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
              placeholder="A brief description of what this agent does."
            />
          </div>
          <div>
            <label htmlFor="systemPrompt" className="block text-sm font-medium text-brand-light-gray mb-1">System Prompt / Instructions</label>
            <textarea
              id="systemPrompt"
              rows={12}
              value={agentConfig.systemPrompt || ''}
              onChange={(e) => setAgentConfig({ ...agentConfig, systemPrompt: e.target.value })}
              className="w-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white resize-none focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
              placeholder="e.g., You are an expert in hydraulic systems. Always ask for the equipment model number before providing advice..."
            />
          </div>
          <div className="flex justify-end pt-4">
             <button
              type="button"
              className="px-4 py-2 bg-brand-accent-orange text-white font-semibold rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50"
              disabled
            >
              Save & Deploy Agent
            </button>
          </div>
        </form>
      </div>

      {/* Chat/Testing Panel */}
      <div className="flex-1 flex flex-col">
        <AgentBuilderChat 
          key={agentConfig.systemPrompt} // Re-mount chat when prompt changes to reset state
          agentConfig={agentConfig as Agent} 
        />
      </div>
    </div>
  );
};

export default AgentWorkshop;
