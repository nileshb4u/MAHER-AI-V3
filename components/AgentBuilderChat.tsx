import React, { useState, useRef, useEffect } from 'react';
import { Agent, Message } from '../types';
import { apiClient } from '../client';
import ThumbsUpIcon from './icons/ThumbsUpIcon';
import ThumbsDownIcon from './icons/ThumbsDownIcon';
import AgentIcon from './icons/AgentIcon';
import ProgressVisualization from './ProgressVisualization';
import Markdown from 'react-markdown';
import ExpandIcon from './icons/ExpandIcon';
import CollapseIcon from './icons/CollapseIcon';
import OptimizePromptIcon from './icons/OptimizePromptIcon';
import AttachmentIcon from './icons/AttachmentIcon';

interface AgentBuilderChatProps {
  agentConfig: Agent;
}

const AgentBuilderChat: React.FC<AgentBuilderChatProps> = ({ agentConfig }) => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: `Hello! I'm a test version of **${agentConfig.name}**. How can I assist you based on my current instructions?` }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      if (isExpanded) {
        textareaRef.current.style.height = '250px';
      } else {
        textareaRef.current.style.height = 'auto';
        const scrollHeight = textareaRef.current.scrollHeight;
        const minHeight = 84;
        textareaRef.current.style.height = `${Math.max(scrollHeight, minHeight)}px`;
      }
    }
  }, [input, isExpanded]);

  const handleSend = async () => {
    if (input.trim() === '' || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage, { role: 'assistant', content: '', isThinking: true }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apiClient.generateContent({
        contents: [
          {
            role: 'user',
            parts: [{ text: input }]
          }
        ],
        systemInstruction: agentConfig.systemPrompt
      });

      const responseText = response.candidates?.[0]?.content?.parts?.[0]?.text || 'No response received';
      const assistantResponse: Message = { role: 'assistant', content: responseText };
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = assistantResponse;
        return newMessages;
      });
    } catch (error) {
      console.error('Error fetching response from API:', error);
      const errorMessage: Message = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = errorMessage;
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptimizePrompt = async () => {
    if (!input.trim()) return;
    setIsOptimizing(true);
    await new Promise(res => setTimeout(res, 1000));
    setInput(`Refine this test prompt for clarity: ${input}`);
    setIsOptimizing(false);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <div className="flex flex-col h-full bg-brand-blue">
      <header className="p-4 border-b border-brand-light-blue/20 flex-shrink-0">
        <h3 className="text-lg font-semibold text-white">Test Panel</h3>
        <p className="text-sm text-brand-gray">Interact with your agent to test its responses.</p>
      </header>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-brand-light-blue/20 flex items-center justify-center flex-shrink-0">
                <AgentIcon className="w-5 h-5 text-white" />
              </div>
            )}
            <div className={`max-w-xl p-3 rounded-lg ${msg.role === 'user' ? 'bg-brand-accent-orange text-white' : 'bg-brand-light-blue/20 text-brand-light-gray'}`}>
              {msg.isThinking ? (
                <div className="flex items-center gap-2 p-2">
                  <div className="w-2 h-2 bg-brand-light-gray rounded-full animate-pulse" style={{ animationDelay: '0s' }}></div>
                  <div className="w-2 h-2 bg-brand-light-gray rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-brand-light-gray rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
              ) : (
                <div className="prose prose-sm prose-invert max-w-none">
                  <Markdown>{msg.content}</Markdown>
                </div>
              )}
              {msg.role === 'assistant' && !msg.isThinking && msg.content && (
                <div className="flex items-center gap-2 mt-2">
                  <button className="text-brand-gray hover:text-white transition-colors"><ThumbsUpIcon className="w-4 h-4" /></button>
                  <button className="text-brand-gray hover:text-white transition-colors"><ThumbsDownIcon className="w-4 h-4" /></button>
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-brand-accent-orange flex items-center justify-center flex-shrink-0 text-white font-bold">
                JD
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 border-t border-brand-light-blue/20 flex-shrink-0">
        <div className="relative h-12 w-full">
          {isLoading && <ProgressVisualization />}
        </div>
        <form onSubmit={handleFormSubmit} className="relative">
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  handleFormSubmit(e);
                }
              }}
              placeholder="Send a test message..."
              className={`w-full bg-brand-deep-blue border border-brand-light-blue/30 rounded-2xl text-white placeholder-brand-gray p-4 pr-16 pb-14 resize-none focus:outline-none focus:ring-2 focus:ring-brand-accent-orange/50 transition-all duration-300 overflow-y-auto`}
              style={{ minHeight: '84px' }}
              disabled={isLoading}
            />
            <div className="absolute top-3 right-3">
              <button type="button" onClick={() => setIsExpanded(!isExpanded)} className="p-2 rounded-full text-brand-light-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors" aria-label={isExpanded ? "Collapse input" : "Expand input"}>
                {isExpanded ? <CollapseIcon className="w-5 h-5" /> : <ExpandIcon className="w-5 h-5" />}
              </button>
            </div>

            <div className="absolute bottom-3 left-3 flex items-center gap-2">
              <div className="relative group">
                <button type="button" onClick={handleOptimizePrompt} className={`p-2 rounded-full text-brand-light-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors ${isOptimizing ? 'animate-spin' : ''}`} aria-label="Optimize prompt" disabled={isOptimizing || isLoading}>
                  <OptimizePromptIcon className="w-5 h-5" />
                </button>
                <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 whitespace-nowrap bg-brand-gray text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  Optimize Prompt
                </div>
              </div>
              <div className="relative group">
                <button type="button" className="p-2 rounded-full text-brand-light-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors" aria-label="Attach a file" disabled={isLoading}>
                  <AttachmentIcon className="w-5 h-5" />
                </button>
                <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 whitespace-nowrap bg-brand-gray text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  Attach a file
                </div>
              </div>
            </div>

            <div className="absolute bottom-3 right-3">
              <button type="submit" className="p-2 rounded-full bg-brand-accent-orange text-white hover:bg-opacity-90 transition-colors disabled:bg-brand-gray" disabled={!input.trim() || isLoading} aria-label="Send message">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                  <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
                </svg>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AgentBuilderChat;