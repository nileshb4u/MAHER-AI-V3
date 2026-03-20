import React, { useEffect, useState } from 'react';
import { Agent } from '../types';
import AgentChat from './AgentChat';

interface AgentModalProps {
  agent: Agent;
  onClose: () => void;
}

const AgentModal: React.FC<AgentModalProps> = ({ agent, onClose }) => {
  const [isClosing, setIsClosing] = useState(false);

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
              <h2 className="text-lg font-bold text-white">{agent.name}</h2>
              <p className="text-xs text-brand-gray">{agent.displayProviderName}</p>
            </div>
          </div>
          <button onClick={handleClose} className="p-2 rounded-full text-brand-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>
        <div className="flex-1 overflow-y-auto">
          <AgentChat agent={agent} />
        </div>
      </div>
    </div>
  );
};

export default AgentModal;
