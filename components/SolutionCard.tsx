import React from 'react';
import { Agent } from '../types';

interface SolutionCardProps {
  agent: Agent;
  onLaunch: (agent: Agent) => void;
}

const SolutionCard: React.FC<SolutionCardProps> = ({ agent, onLaunch }) => {

  const getStatusClasses = (statusClass: string) => {
    switch (statusClass) {
      case 'available':
        return 'bg-green-500/10 text-green-400 border-green-500/30';
      case 'development':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
      case 'poc':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/30';
    }
  }

  return (
    <div className="bg-brand-blue border border-brand-light-blue/20 rounded-2xl p-6 flex flex-col h-full transition-all duration-300 hover:border-brand-accent-orange/50 hover:-translate-y-1 hover:shadow-2xl hover:shadow-brand-accent-orange/10">
      <div className="flex justify-between items-start mb-4">
        <div 
          style={{ backgroundColor: agent.iconBackgroundColor }}
          className="w-12 h-12 rounded-lg flex items-center justify-center text-white flex-shrink-0"
          dangerouslySetInnerHTML={{ __html: agent.iconSVG }}
        />
        <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${getStatusClasses(agent.statusClass)}`}>
          {agent.statusText}
        </span>
      </div>
      <div className="flex-grow">
        <h3 className="text-xl font-bold text-white mb-2">{agent.name}</h3>
        <p className="text-brand-gray text-sm leading-relaxed">{agent.description}</p>
      </div>
      <div className="mt-6">
        <button onClick={() => onLaunch(agent)} className="w-full text-center bg-brand-light-blue/20 text-white font-semibold py-2.5 rounded-lg transition-colors hover:bg-brand-accent-orange hover:text-brand-deep-blue">
          Launch Assistant
        </button>
      </div>
    </div>
  );
};

export default SolutionCard;
