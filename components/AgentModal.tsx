import React, { useEffect, useState } from 'react';
import { Agent } from '../types';
import AgentChat from './AgentChat';

interface AgentModalProps {
  agent: Agent;
  onClose: () => void;
}

const AgentModal: React.FC<AgentModalProps> = ({ agent, onClose }) => {
  const [isClosing, setIsClosing] = useState(false);
  const [showSkillSchema, setShowSkillSchema] = useState(false);

  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleEsc);
    document.body.style.overflow = 'hidden';

    return () => {
      window.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'auto';
    };
  }, []);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(onClose, 300); // Wait for animation to finish
  };

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-brand-deep-blue/70 backdrop-blur-sm transition-opacity duration-300 ${isClosing ? 'opacity-0' : 'opacity-100'}`}
      onClick={handleClose}
    >
      <div
        className={`bg-brand-blue border border-brand-light-blue/20 rounded-2xl shadow-2xl w-[95%] md:w-3/4 lg:w-2/3 max-w-4xl h-[90%] flex flex-col transition-transform duration-300 ${isClosing ? 'scale-95' : 'scale-100'}`}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between p-4 border-b border-brand-light-blue/20 flex-shrink-0">
          <div className="flex items-center gap-3">
             <div 
                style={{ backgroundColor: agent.iconBackgroundColor }}
                className="w-10 h-10 rounded-lg flex items-center justify-center text-white flex-shrink-0"
                dangerouslySetInnerHTML={{ __html: agent.iconSVG }}
              />
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">{agent.name}</h2>
                {agent.isSkill && (
                  <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-purple-500/15 text-purple-400 border border-purple-500/30 flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Skill
                  </span>
                )}
              </div>
              <p className="text-xs text-brand-gray">{agent.displayProviderName}</p>
            </div>
          </div>
          {/* Skill schema toggle */}
          {agent.isSkill && agent.toolSchema && (
            <button
              onClick={() => setShowSkillSchema(!showSkillSchema)}
              className="mr-2 px-3 py-1.5 text-xs bg-purple-500/15 border border-purple-500/30 text-purple-400 rounded-lg hover:bg-purple-500/25 transition-colors flex items-center gap-1.5"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              {showSkillSchema ? 'Hide Schema' : 'View Schema'}
            </button>
          )}
          <button onClick={handleClose} className="p-2 rounded-full text-brand-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>
        {showSkillSchema && agent.toolSchema && (
          <div className="border-b border-brand-light-blue/20 bg-brand-deep-blue/50 p-4">
            <h4 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              Skill Interface — {agent.toolSchema.function.name}
            </h4>
            <p className="text-xs text-brand-gray mb-3">{agent.toolSchema.function.description}</p>
            {agent.toolSchema.function.parameters?.properties && (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-brand-light-gray">Parameters:</p>
                {Object.entries(agent.toolSchema.function.parameters.properties).map(([pname, pdef]) => (
                  <div key={pname} className="flex items-start gap-2 text-xs">
                    <span className="font-mono text-purple-300 bg-purple-500/10 px-1.5 py-0.5 rounded flex-shrink-0">
                      {pname}
                      {agent.toolSchema!.function.parameters.required?.includes(pname) && (
                        <span className="text-red-400 ml-0.5">*</span>
                      )}
                    </span>
                    <span className="text-brand-gray/80 italic">{(pdef as any).type}</span>
                    <span className="text-brand-gray">{(pdef as any).description}</span>
                  </div>
                ))}
                <p className="text-xs text-brand-gray/50 mt-1">* required</p>
              </div>
            )}
          </div>
        )}
        <div className="flex-1 overflow-y-auto">
          <AgentChat agent={agent} />
        </div>
      </div>
    </div>
  );
};

export default AgentModal;
