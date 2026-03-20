import React, { useState } from 'react';

const FAQItem = ({ question, answer }: { question: string; answer: string }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-brand-light-blue/20 rounded-lg bg-brand-blue/30 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full p-4 text-left hover:bg-brand-light-blue/10 transition-colors"
      >
        <span className="font-semibold text-white">{question}</span>
        <svg
          className={`w-5 h-5 text-brand-accent-orange transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && (
        <div className="p-4 pt-0 text-brand-gray text-sm leading-relaxed border-t border-brand-light-blue/10">
          {answer}
        </div>
      )}
    </div>
  );
};

const Help: React.FC = () => {
  return (
    <div className="p-6 md:p-8 space-y-12 text-white h-full overflow-y-auto pb-20">
      {/* Header Section */}
      <div className="text-center max-w-4xl mx-auto mt-4">
        <h1 className="text-4xl md:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-brand-accent-blue">
          How can MAHER help you today?
        </h1>
        <p className="text-brand-gray text-lg max-w-2xl mx-auto">
          Your intelligent assistant for maintenance, automation, and beyond. Explore our guides to unlock the full potential of MAHER AI.
        </p>
      </div>

      {/* Quick Start Guides Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {/* Guide 1: Chat & Voice */}
        <div className="bg-gradient-to-br from-brand-blue/80 to-brand-deep-blue border border-brand-light-blue/20 rounded-xl p-6 shadow-lg hover:shadow-brand-accent-blue/10 hover:border-brand-accent-blue/30 transition-all duration-300 group">
          <div className="w-14 h-14 bg-blue-500/10 rounded-2xl flex items-center justify-center mb-6 border border-blue-500/20 group-hover:scale-105 transition-transform">
            <svg className="w-7 h-7 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-3 text-white">Chat & Voice</h3>
          <p className="text-brand-gray text-sm mb-5 leading-relaxed">
            Interact naturally with MAHER using real-time text or voice commands.
          </p>
          <ul className="space-y-3">
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-2"></span>
              <span>Type your query in the chat bar at the bottom.</span>
            </li>
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-2"></span>
              <span>Click the 🎤 icon to speak your command hands-free.</span>
            </li>
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-2"></span>
              <span>Use <strong>New Chat</strong> to start a fresh conversation context.</span>
            </li>
          </ul>
        </div>

        {/* Guide 2: Agent Studio */}
        <div className="bg-gradient-to-br from-brand-blue/80 to-brand-deep-blue border border-brand-light-blue/20 rounded-xl p-6 shadow-lg hover:shadow-purple-500/10 hover:border-purple-500/30 transition-all duration-300 group">
          <div className="w-14 h-14 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-6 border border-purple-500/20 group-hover:scale-105 transition-transform">
            <svg className="w-7 h-7 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-3 text-white">Agent Studio</h3>
          <p className="text-brand-gray text-sm mb-5 leading-relaxed">
            Create or customize specialized AI agents for specific tasks.
          </p>
          <ul className="space-y-3">
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-2"></span>
              <span>Design a new agent with a custom name and instructions.</span>
            </li>
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-2"></span>
              <span><strong>Guests:</strong> Agents are saved as 'Drafts' for admin review.</span>
            </li>
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-2"></span>
              <span>Access your drafts anytime via the <strong>Actions</strong> menu.</span>
            </li>
          </ul>
        </div>

        {/* Guide 3: Solutions & Tools */}
        <div className="bg-gradient-to-br from-brand-blue/80 to-brand-deep-blue border border-brand-light-blue/20 rounded-xl p-6 shadow-lg hover:shadow-green-500/10 hover:border-green-500/30 transition-all duration-300 group">
          <div className="w-14 h-14 bg-green-500/10 rounded-2xl flex items-center justify-center mb-6 border border-green-500/20 group-hover:scale-105 transition-transform">
            <svg className="w-7 h-7 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-3 text-white">Tools & Solutions</h3>
          <p className="text-brand-gray text-sm mb-5 leading-relaxed">
            Leverage pre-built RPA solutions for complex workflow automation.
          </p>
          <ul className="space-y-3">
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-2"></span>
              <span>Visit <strong>Solutions Overview</strong> to see available automations.</span>
            </li>
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-2"></span>
              <span>Use the <strong>Toolroom</strong> for specialized utility scripts.</span>
            </li>
            <li className="flex items-start gap-3 text-sm text-brand-light-gray">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-2"></span>
              <span>Monitor execution results in real-time.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="max-w-3xl mx-auto pt-8">
        <h2 className="text-2xl font-bold mb-6 text-center text-white">Frequently Asked Questions</h2>
        <div className="grid gap-4">
          <FAQItem
            question="Why can't I see the agent I just created?"
            answer="If you are using a guest account, your agents are saved as 'Drafts' strictly for security reasons. They will not appear in the public list until an Administrator reviews and publishes them. You can view your own drafts in the 'Actions' menu."
          />
          <FAQItem
            question="How do I switch between different Agents?"
            answer="You can navigate to the 'Agent Studio' or the home page sidebar to select different AI agents. Each agent is optimized for different tasks (e.g., Coding, Writing, Maintenance Support)."
          />
          <FAQItem
            question="My voice commands aren't being picked up."
            answer="Please ensure you have granted microphone permissions to the browser. Click the lock icon in your address bar to verify settings. Also, check that your input device is correctly selected in your system sound settings."
          />
          <FAQItem
            question="How do I request Admin access?"
            answer="Admin access is restricted to authorized personnel. If you believe you need these permissions for your role, please contact the IT Support team or your system administrator directly."
          />
        </div>
      </div>

      {/* Contact Support */}
      <div className="mt-12 text-center border-t border-brand-light-blue/10 pt-8">
        <p className="text-brand-gray">Still need help?</p>
        <a href="#" className="text-brand-accent-orange font-semibold hover:underline mt-2 inline-block">Contact Support</a>
      </div>
    </div>
  );
};

export default Help;
