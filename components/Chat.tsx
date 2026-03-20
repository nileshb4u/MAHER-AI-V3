import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types';
import { SUGGESTED_QUESTIONS } from '../constants';
import { apiClient } from '../client';
import ThumbsUpIcon from './icons/ThumbsUpIcon';
import ThumbsDownIcon from './icons/ThumbsDownIcon';
import AgentIcon from './icons/AgentIcon';
import ProgressVisualization from './ProgressVisualization';
import ThinkingProcess from './ThinkingProcess';
import Markdown from 'react-markdown';
import ExpandIcon from './icons/ExpandIcon';
import CollapseIcon from './icons/CollapseIcon';
import OptimizePromptIcon from './icons/OptimizePromptIcon';
import AttachmentIcon from './icons/AttachmentIcon';

interface ChatProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

const Chat: React.FC<ChatProps> = ({ messages, setMessages }) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    if (messages.length === 2 && messages[1].role === 'user' && !isLoading) {
      handleSend(messages[1].content, true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      if (isExpanded) {
        textareaRef.current.style.height = '250px';
      } else {
        textareaRef.current.style.height = 'auto'; // Reset height
        const scrollHeight = textareaRef.current.scrollHeight;
        const minHeight = 84; // Corresponds to min-h-[84px]
        textareaRef.current.style.height = `${Math.max(scrollHeight, minHeight)}px`;
      }
    }
  }, [input, isExpanded]);

  const handleSend = async (messageContent: string, isInitialMessage = false) => {
    if (messageContent.trim() === '' || isLoading) return;

    if (!isInitialMessage) {
      const userMessage: Message = { role: 'user', content: messageContent };
      setMessages(prev => [...prev, userMessage]);
    }

    setMessages(prev => [...prev, { role: 'assistant', content: '', isThinking: true }]);
    const currentInput = input;
    const currentFiles = [...attachedFiles];
    if (input) setInput('');
    setAttachedFiles([]); // Clear attached files after sending
    setIsLoading(true);

    try {
      let responseText = '';
      let thinkingProcess: any = undefined;
      let skillsUsed: string[] | undefined;

      // If files are attached, use the hybrid orchestrator file upload endpoint
      if (currentFiles.length > 0) {
        const formData = new FormData();
        formData.append('input', messageContent);
        currentFiles.forEach(file => formData.append('files', file));

        const resp = await fetch('/api/hybrid-orchestrator/process-with-files', {
          method: 'POST',
          body: formData,
        });
        if (!resp.ok) throw new Error('Orchestrator request failed');
        const data = await resp.json();
        responseText = data.answer || `Sorry, could not process the uploaded files.`;
        thinkingProcess = data.thinking_process;
      } else {
        // Text-only: try skills orchestrator first, fall back to hybrid
        let skillsData: any = null;
        try {
          const skillsResp = await fetch('/api/skills-orchestrator/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageContent, history: [] }),
          });
          if (skillsResp.ok) {
            skillsData = await skillsResp.json();
          }
        } catch (_) {
          // skills orchestrator unavailable, fall through
        }

        if (skillsData?.success && skillsData?.answer) {
          responseText = skillsData.answer;
          thinkingProcess = skillsData.thinking_process;
          skillsUsed = skillsData.skills_used?.length ? skillsData.skills_used : undefined;
        } else {
          // Fall back to hybrid orchestrator
          const hybridResp = await fetch('/api/hybrid-orchestrator/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: messageContent }),
          });
          if (!hybridResp.ok) throw new Error('Orchestrator request failed');
          const hybridData = await hybridResp.json();
          if (hybridData.success) {
            responseText = hybridData.answer || 'No response generated.';
            thinkingProcess = hybridData.thinking_process;
          } else {
            responseText = `Sorry, the orchestrator encountered an error: ${hybridData.error || 'Unknown error'}`;
          }
        }
      }

      const assistantResponse: Message = {
        role: 'assistant',
        content: responseText,
        thinking_process: thinkingProcess,
        skillsUsed,
      };
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

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(input);
  };

  const handleOptimizePrompt = async () => {
    if (!input.trim()) return;
    setIsOptimizing(true);

    try {
      const response = await apiClient.generateContent({
        contents: [
          {
            role: 'user',
            parts: [{
              text: input
            }]
          }
        ],
        systemInstruction: "You are the Prompt Optimization Assistant within the MAHER AI ecosystem. Your job is to refine and restructure user prompts so they are clear, specific, and well-formatted for the AI model to understand. Do not answer questions or provide solutions. Only output the optimized version of the user's prompt. Preserve the original intent and tone. Clarify and simplify wording where needed. Add structure such as context, task, and expected output when appropriate. Only include maintenance, engineering, or analytical context if the user's wording clearly indicates that domain; otherwise remain neutral. Never insert external data or assumptions. If the user's prompt is already clear and optimal, respond with: 'Your prompt is already clear and optimized. No changes needed.'"
      });

      const optimizedPrompt = response.candidates?.[0]?.content?.parts?.[0]?.text || input;

      // If the response indicates no changes needed, keep original
      if (optimizedPrompt.includes('already clear and optimized')) {
        setInput(input);
      } else {
        setInput(optimizedPrompt.trim());
      }
    } catch (error) {
      console.error('Error optimizing prompt:', error);
      // Fallback to basic enhancement if API fails
      setInput(`Please refine my following question for clarity and detail, then provide the answer: ${input}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const maxSize = 2 * 1024 * 1024; // 2 MB in bytes

    // Validate each file
    const validFiles: File[] = [];
    const errors: string[] = [];

    files.forEach(file => {
      if (file.size > maxSize) {
        errors.push(`${file.name} exceeds 2 MB limit (${(file.size / (1024 * 1024)).toFixed(2)} MB)`);
      } else {
        validFiles.push(file);
      }
    });

    if (errors.length > 0) {
      alert(`Some files were not added:\n${errors.join('\n')}`);
    }

    if (validFiles.length > 0) {
      setAttachedFiles(prev => [...prev, ...validFiles]);
    }

    // Reset input to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemoveFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const showSuggestions = messages.length <= 1;

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full">
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-brand-blue flex items-center justify-center flex-shrink-0 border border-brand-light-blue/20">
                <AgentIcon className="w-5 h-5 text-brand-accent-orange" />
              </div>
            )}
            <div className={`max-w-2xl ${msg.role === 'user' ? '' : 'w-full'}`}>
              {/* Thinking Process - Show before message content for assistant */}
              {msg.role === 'assistant' && !msg.isThinking && msg.thinking_process && (
                <ThinkingProcess thinkingTrail={msg.thinking_process} />
              )}

              <div className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-brand-accent-orange text-white' : 'bg-brand-light-blue/20 text-brand-light-gray'}`}>
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
                {msg.role === 'assistant' && !msg.isThinking && msg.skillsUsed && msg.skillsUsed.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2 pt-2 border-t border-brand-light-blue/10">
                    <span className="text-xs text-brand-gray">Skills used:</span>
                    {msg.skillsUsed.map((skill, si) => (
                      <span key={si} className="px-2 py-0.5 text-xs bg-purple-500/15 text-purple-400 border border-purple-500/25 rounded-full flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-2.5 w-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        {skill}
                      </span>
                    ))}
                  </div>
                )}
                {msg.role === 'assistant' && !msg.isThinking && msg.content && (
                  <div className="flex items-center gap-2 mt-2">
                    <button className="text-brand-gray hover:text-white transition-colors"><ThumbsUpIcon className="w-4 h-4" /></button>
                    <button className="text-brand-gray hover:text-white transition-colors"><ThumbsDownIcon className="w-4 h-4" /></button>
                  </div>
                )}
              </div>
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-brand-accent-orange flex items-center justify-center flex-shrink-0 text-white font-bold">
                JD
              </div>
            )}
          </div>
        ))}
        {showSuggestions && (
          <div className="pt-8 text-center">
            <h3 className="text-sm font-semibold text-brand-gray mb-3">Try asking one of these:</h3>
            <div className="flex flex-wrap justify-center gap-3">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button key={i} onClick={() => handleSend(q)} className="p-3 bg-brand-light-blue/10 rounded-lg text-left text-sm hover:bg-brand-light-blue/20 transition-colors text-brand-light-gray">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 flex-shrink-0">
        <div className="relative h-12 w-full">
          {isLoading && <ProgressVisualization />}
        </div>
        <form onSubmit={handleFormSubmit} className="relative">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.xls,.xlsx"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Attached files display */}
          {attachedFiles.length > 0 && (
            <div className="mb-3">
              <div className="flex flex-wrap gap-2 mb-2">
                {attachedFiles.map((file, index) => (
                  <div key={index} className="flex items-center gap-2 bg-brand-light-blue/20 px-3 py-2 rounded-lg text-sm text-brand-light-gray">
                    <span className="truncate max-w-[200px]">{file.name}</span>
                    <span className="text-xs text-brand-gray">({(file.size / 1024).toFixed(1)} KB)</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(index)}
                      className="text-brand-gray hover:text-white transition-colors"
                      aria-label="Remove file"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                        <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
              <div className="text-xs text-brand-gray italic">
                Files will be analyzed and sent with your message. Max 2 MB per file.
              </div>
            </div>
          )}

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
              placeholder="Ask a follow-up question..."
              className={`w-full bg-brand-blue border border-brand-light-blue/30 rounded-2xl text-white placeholder-brand-gray p-4 pr-16 pb-14 resize-none focus:outline-none focus:ring-2 focus:ring-brand-accent-orange/50 transition-all duration-300 overflow-y-auto`}
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
                <button type="button" onClick={handleAttachClick} className="p-2 rounded-full text-brand-light-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors" aria-label="Attach a file" disabled={isLoading}>
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

export default Chat;