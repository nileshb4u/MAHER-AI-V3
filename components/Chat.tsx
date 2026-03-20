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
      let orchestratorResponse;

      // If files are attached, use the file upload endpoint
      if (currentFiles.length > 0) {
        const formData = new FormData();
        formData.append('input', messageContent);

        // Add all attached files
        currentFiles.forEach(file => {
          formData.append('files', file);
        });

        // Send to orchestrator with files
        orchestratorResponse = await fetch('/api/hybrid-orchestrator/process-with-files', {
          method: 'POST',
          body: formData  // Don't set Content-Type - browser sets it with boundary
        });
      } else {
        // No files - use regular JSON endpoint
        orchestratorResponse = await fetch('/api/hybrid-orchestrator/process', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            input: messageContent
          })
        });
      }

      if (!orchestratorResponse.ok) {
        throw new Error('Orchestrator request failed');
      }

      const orchestratorData = await orchestratorResponse.json();

      // Format response from hybrid orchestrator
      let responseText = '';

      if (orchestratorData.success) {
        // NEW: Use the compiled answer if available
        if (orchestratorData.answer) {
          responseText = orchestratorData.answer;
        } else {
          // Fallback to old manual parsing (for backwards compatibility)
          const execution = orchestratorData.execution_summary;
          const results = orchestratorData.results?.results || [];

          // Show orchestrator header with resources used
          if (results.length > 0) {
            const resourcesUsed = results.map((r: any) => {
              const type = r.type === 'workflow' ? '⚙️' : r.type === 'tool' ? '🔧' : '🤖';
              return `${type} ${r.resource}`;
            });

            responseText += `**🎯 MAHER Hybrid Orchestrator**\n`;
            responseText += `Strategy: ${execution?.strategy || 'sequential'} | `;
            responseText += `Subtasks: ${execution?.successful || 0}/${execution?.total_subtasks || 0} successful\n`;
            responseText += `Resources: ${resourcesUsed.join(', ')}\n`;

            // Show files processed if any
            if (orchestratorData.files_processed && orchestratorData.files_processed.length > 0) {
              const filesInfo = orchestratorData.files_processed.map((f: any) => f.filename).join(', ');
              responseText += `Files: ${filesInfo}\n`;
            }

            responseText += `\n---\n\n`;
          }

          // Format results
          for (const result of results) {
            const data = result.data;

            if (data?.success) {
              // Handle workflow/tool results
              if (result.type === 'workflow' || result.type === 'tool') {
                responseText += `### ${result.resource}\n\n`;

                // Format different types of data
                if (data.checklist_items) {
                  responseText += `**Checklist Items:**\n`;
                  data.checklist_items.forEach((item: string, idx: number) => {
                    responseText += `${idx + 1}. ${item}\n`;
                  });
                  responseText += `\n`;

                  if (data.safety_notes && data.safety_notes.length > 0) {
                    responseText += `**Safety Notes:**\n`;
                    data.safety_notes.forEach((note: string) => responseText += `- ${note}\n`);
                    responseText += `\n`;
                  }

                  if (data.required_tools && data.required_tools.length > 0) {
                    responseText += `**Required Tools:**\n`;
                    data.required_tools.forEach((tool: string) => responseText += `- ${tool}\n`);
                    responseText += `\n`;
                  }

                  if (data.estimated_duration_hours) {
                    responseText += `**Estimated Duration:** ${data.estimated_duration_hours} hours\n\n`;
                  }
                } else if (data.equipment_id || data.name) {
                  responseText += `**Equipment:** ${data.name || data.equipment_id}\n`;
                  if (data.manufacturer) responseText += `**Manufacturer:** ${data.manufacturer}\n`;
                  if (data.model) responseText += `**Model:** ${data.model}\n`;
                  if (data.location) responseText += `**Location:** ${data.location}\n`;
                  if (data.criticality) responseText += `**Criticality:** ${data.criticality}\n`;
                  responseText += `\n`;
                } else if (data.total_cost) {
                  responseText += `**Cost Estimate:**\n`;
                  responseText += `- Labor: $${data.cost_breakdown?.labor?.total || 0}\n`;
                  responseText += `- Parts: $${data.cost_breakdown?.parts || 0}\n`;
                  responseText += `- Downtime: $${data.cost_breakdown?.downtime || 0}\n`;
                  responseText += `- **Total: $${data.total_cost}**\n`;
                  responseText += `- Confidence: ${data.confidence_level}\n\n`;
                } else if (data.identified_root_causes) {
                  responseText += `**Root Causes:**\n`;
                  data.identified_root_causes.forEach((cause: string) => responseText += `- ${cause}\n`);
                  responseText += `\n`;

                  if (data.recommendations && data.recommendations.length > 0) {
                    responseText += `**Recommendations:**\n`;
                    data.recommendations.forEach((rec: any) => {
                      responseText += `- [${rec.priority}] ${rec.action}\n`;
                    });
                    responseText += `\n`;
                  }
                } else if (data.results) {
                  responseText += `Found ${data.total_results || 0} results\n\n`;
                  if (data.results.length > 0) {
                    data.results.slice(0, 5).forEach((doc: any) => {
                      responseText += `- **${doc.title}** (${doc.type}) - Rev ${doc.revision}\n`;
                    });
                  }
                } else if (data.output_file || data.text || data.tables) {
                  // Document processing results (PDF, Word, Excel, OCR)
                  if (data.output_file) {
                    responseText += `✅ **File created:** ${data.output_file}\n`;
                    if (data.pages) responseText += `📄 **Pages:** ${data.pages}\n`;
                    if (data.size) responseText += `💾 **Size:** ${(data.size / 1024).toFixed(2)} KB\n`;
                  }
                  if (data.text) {
                    const preview = data.text.substring(0, 200);
                    responseText += `**Extracted text:**\n${preview}${data.text.length > 200 ? '...' : ''}\n`;
                  }
                  if (data.tables && data.tables.length > 0) {
                    responseText += `**Extracted tables:** ${data.tables.length} table(s)\n`;
                  }
                  if (data.rows) responseText += `**Rows:** ${data.rows}\n`;
                  if (data.columns) responseText += `**Columns:** ${data.columns}\n`;
                  responseText += `\n`;
                } else {
                  // Generic data display
                  responseText += JSON.stringify(data, null, 2) + '\n\n';
                }
              } else if (result.type === 'ai_agent') {
                // AI agent response
                responseText += data.response || '';
              }
            } else {
              responseText += `⚠️ ${result.resource} encountered an error\n\n`;
            }
          }

          // Show incomplete tasks if any
          if (orchestratorData.results?.incomplete_tasks?.length > 0) {
            responseText += `\n---\n\n`;
            responseText += `**⚠️ Incomplete Tasks:**\n`;
            orchestratorData.results.incomplete_tasks.forEach((task: any) => {
              responseText += `- ${task.resource}: ${task.error}\n`;
            });
          }
        }
      } else {
        // Error response
        responseText = `Sorry, the orchestrator encountered an error: ${orchestratorData.error || 'Unknown error'}`;
      }

      const assistantResponse: Message = {
        role: 'assistant',
        content: responseText,
        thinking_process: orchestratorData.thinking_process  // Include thinking trail
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