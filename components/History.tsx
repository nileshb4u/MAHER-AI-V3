
import React from 'react';
import { Message } from '../types';

interface HistoryProps {
  history: Message[][];
  onViewConversation: (conversation: Message[]) => void;
}

const History: React.FC<HistoryProps> = ({ history, onViewConversation }) => {
  return (
    <div className="p-4 md:p-8 text-white">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold">Conversation History</h1>
          <p className="text-lg text-brand-gray mt-2">
            Review and continue your past conversations with MAHER AI.
          </p>
        </header>

        {history.length === 0 ? (
          <div className="mt-8 p-12 border-2 border-dashed border-brand-light-blue/30 rounded-lg text-center">
            <svg className="mx-auto h-12 w-12 text-brand-gray" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h2 className="mt-4 text-2xl font-semibold text-brand-light-gray">No History Yet</h2>
            <p className="text-brand-gray mt-2">Your completed conversations will appear here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((conversation, index) => {
              const firstUserMessage = conversation.find(msg => msg.role === 'user');
              const title = firstUserMessage ? firstUserMessage.content : 'Untitled Conversation';
              const lastMessage = conversation[conversation.length - 1];
              const preview = lastMessage.isThinking ? 'Assistant is thinking...' : (lastMessage.role === 'assistant' ? lastMessage.content : `You: ${lastMessage.content}`);
              
              return (
                <button
                  key={index}
                  onClick={() => onViewConversation(conversation)}
                  className="w-full text-left bg-brand-light-blue/10 p-4 rounded-lg border border-transparent hover:border-brand-accent-orange/50 transition-all group"
                >
                  <div className="flex flex-col">
                      <h3 className="font-semibold text-white truncate group-hover:text-brand-accent-orange transition-colors">{title}</h3>
                      <p className="text-sm text-brand-gray mt-1 truncate">{preview}</p>
                      <p className="text-xs text-brand-gray/70 mt-2 self-end">{conversation.length} messages</p>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
