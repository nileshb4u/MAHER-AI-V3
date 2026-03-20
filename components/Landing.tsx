import React, { useState, useRef, useEffect } from 'react';
import { AppView } from '../types';
import { LANDING_TILES, INITIAL_ASSISTANT_MESSAGE } from '../constants';
import { apiClient } from '../client';
import ExpandIcon from './icons/ExpandIcon';
import CollapseIcon from './icons/CollapseIcon';
import OptimizePromptIcon from './icons/OptimizePromptIcon';
import AttachmentIcon from './icons/AttachmentIcon';


interface LandingProps {
    onStartChat: (firstMessage: string) => void;
    setCurrentView: (view: AppView) => void;
}

const Landing: React.FC<LandingProps> = ({ onStartChat, setCurrentView }) => {
    const [input, setInput] = useState('');
    const [isExpanded, setIsExpanded] = useState(false);
    const [isOptimizing, setIsOptimizing] = useState(false);
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFormSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim()) {
            onStartChat(input);
            setInput('');
        }
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
            setInput(`Provide a detailed, step-by-step maintenance procedure for the following task, including all necessary safety precautions and required tools: ${input}`);
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


    return (
        <div className="flex flex-col lg:flex-row items-center justify-center h-full p-4 text-center relative overflow-hidden">
            {/* MAHER Robot Image - Floating on the right side */}
            <div className="hidden lg:block absolute right-0 top-1/2 -translate-y-1/2 opacity-20 hover:opacity-40 transition-opacity duration-500 pointer-events-none">
                <img
                    src="/images/maher-robot.png"
                    alt="MAHER AI Robot"
                    className="h-[600px] w-auto"
                    style={{ filter: 'drop-shadow(0 0 30px rgba(249, 115, 22, 0.3))' }}
                />
            </div>

            {/* Main Content */}
            <div className="max-w-4xl w-full relative z-10">
                {/* Logo - MAHER Face */}
                <div className="flex justify-center mb-6">
                    <div className="relative group">
                        <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-brand-accent-orange/50 shadow-lg shadow-brand-accent-orange/20 transition-all duration-300 group-hover:border-brand-accent-orange group-hover:shadow-xl group-hover:shadow-brand-accent-orange/40">
                            <img
                                src="/images/maher-logo.png"
                                alt="MAHER AI Logo"
                                className="w-full h-full object-cover"
                            />
                        </div>
                        {/* Glow effect */}
                        <div className="absolute inset-0 rounded-full bg-brand-accent-orange/20 blur-xl -z-10 group-hover:bg-brand-accent-orange/30 transition-all duration-300"></div>
                    </div>
                </div>

                {/* Mobile Robot Image - Shows on smaller screens */}
                <div className="lg:hidden flex justify-center mb-6">
                    <img
                        src="/images/maher-robot.png"
                        alt="MAHER AI Robot"
                        className="h-48 w-auto opacity-30"
                    />
                </div>

                <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">MAHER AI</h1>
                <p className="text-lg text-brand-light-gray mb-12 max-w-2xl mx-auto">{INITIAL_ASSISTANT_MESSAGE.split('!')[1].trim()}</p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12 w-full">
                    {LANDING_TILES.map((tile) => (
                        <button
                            key={tile.name}
                            onClick={() => setCurrentView(tile.name)}
                            className="bg-brand-light-blue/10 hover:bg-brand-light-blue/20 p-6 rounded-2xl text-left transition-colors flex flex-col items-start h-full"
                        >
                            <div className="bg-brand-light-blue/20 p-2 rounded-full mb-4">
                                <tile.icon className="w-6 h-6 text-brand-accent-orange" />
                            </div>
                            <h3 className="font-bold text-lg text-white mb-1">{tile.name}</h3>
                            <p className="text-sm text-brand-gray flex-grow">{tile.description}</p>
                        </button>
                    ))}
                </div>

                <div className="w-full mt-8">
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
                                placeholder="Ask MAHER AI about maintenance, schematics, or incident reports..."
                                className={`w-full bg-brand-blue border border-brand-light-blue/30 rounded-2xl text-white placeholder-brand-gray p-4 pr-16 pb-14 resize-none focus:outline-none focus:ring-2 focus:ring-brand-accent-orange/50 transition-all duration-300 overflow-y-auto`}
                                style={{ minHeight: '84px' }}
                            />
                            <div className="absolute top-3 right-3">
                                <button type="button" onClick={() => setIsExpanded(!isExpanded)} className="p-2 rounded-full text-brand-light-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors" aria-label={isExpanded ? "Collapse input" : "Expand input"}>
                                    {isExpanded ? <CollapseIcon className="w-5 h-5" /> : <ExpandIcon className="w-5 h-5" />}
                                </button>
                            </div>

                            <div className="absolute bottom-3 left-3 flex items-center gap-2">
                                <div className="relative group">
                                    <button type="button" onClick={handleOptimizePrompt} className={`p-2 rounded-full text-brand-light-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors ${isOptimizing ? 'animate-spin' : ''}`} aria-label="Optimize prompt" disabled={isOptimizing}>
                                        <OptimizePromptIcon className="w-5 h-5" />
                                    </button>
                                    <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 whitespace-nowrap bg-brand-gray text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                        Optimize Prompt
                                    </div>
                                </div>
                                <div className="relative group">
                                    <button type="button" onClick={handleAttachClick} className="p-2 rounded-full text-brand-light-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors" aria-label="Attach a file">
                                        <AttachmentIcon className="w-5 h-5" />
                                    </button>
                                    <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 whitespace-nowrap bg-brand-gray text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                        Attach a file
                                    </div>
                                </div>
                            </div>

                            <div className="absolute bottom-3 right-3">
                                <button type="submit" className="p-2 rounded-full bg-brand-accent-orange text-white hover:bg-opacity-90 transition-colors disabled:bg-brand-gray" disabled={!input.trim()} aria-label="Send message">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                                        <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Landing;