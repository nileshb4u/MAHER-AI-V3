import React, { useState, useEffect } from 'react';
import { Agent, WizardData, SkillSchema } from '../types';
import AgentBuilderChat from './AgentBuilderChat';
import AgentBuilderWizard from './AgentBuilderWizard';
import { CATEGORY_GUARDRAILS, WIZARD_STEPS } from '../constants';
import { apiClient } from '../client';
import { AdminOnly } from './ProtectedRoute';
import { useAuth } from './AuthProvider';

const initialWizardData: WizardData = {
  category: '',
  taskDefinition: '',
  requiredExpertise: '',
  knowledge: '',
  decisionAuthority: '',
  communicationTone: '',
  detailLevel: '',
  safetyDisclaimers: '',
  escalationPath: '',
  networkId: '',
  department: '',
};

const AgentStudio: React.FC = () => {
  const { isAdmin } = useAuth();
  const [agentName, setAgentName] = useState('New Assistant');
  const [wizardData, setWizardData] = useState<WizardData>(initialWizardData);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [showAssembledPrompt, setShowAssembledPrompt] = useState(false);
  const [savedAgentId, setSavedAgentId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Skill schema state
  const [toolSchema, setToolSchema] = useState<SkillSchema | null>(null);
  const [showSkillSchema, setShowSkillSchema] = useState(false);
  const [isGeneratingSchema, setIsGeneratingSchema] = useState(false);
  const [schemaError, setSchemaError] = useState<string | null>(null);

  useEffect(() => {
    const assemblePrompt = () => {
      const guardrails = wizardData.category ? CATEGORY_GUARDRAILS[wizardData.category] : CATEGORY_GUARDRAILS['other'];

      let assembled = `**AGENT NAME:**\n${agentName}\n\n`;
      assembled += guardrails;

      const sections = WIZARD_STEPS.slice(1).map(step => ({
        title: step.title.toUpperCase(),
        content: wizardData[step.id as keyof Omit<WizardData, 'category'>]
      }));

      assembled += "\n**USER-DEFINED INSTRUCTIONS:**\n";
      sections.forEach(section => {
        if (section.content && section.content.trim()) {
          assembled += `**${section.title}:**\n${section.content}\n\n`;
        }
      });

      setSystemPrompt(assembled.trim());
    };

    assemblePrompt();
  }, [wizardData, agentName]);

  // Auto-hide save messages after 5 seconds
  useEffect(() => {
    if (saveMessage) {
      const timer = setTimeout(() => setSaveMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [saveMessage]);

  // Load agent for editing if coming from About Me page
  useEffect(() => {
    const loadAgentForEditing = async () => {
      const editingAgentId = localStorage.getItem('editingAgentId');
      if (editingAgentId) {
        try {
          const response = await apiClient.getAgent(editingAgentId);
          const agent = response.agent;

          // Set agent data
          setAgentName(agent.name);
          setSavedAgentId(agent.id);

          // Restore skill schema if present
          if (agent.toolSchema) {
            setToolSchema(agent.toolSchema);
          }

          // Parse system prompt back into wizard data
          // This is a basic parser - you may need to enhance it based on your prompt structure
          setWizardData({
            category: agent.category as any,
            taskDefinition: agent.description,
            requiredExpertise: '',
            knowledge: '',
            decisionAuthority: '',
            communicationTone: '',
            detailLevel: '',
            safetyDisclaimers: '',
            escalationPath: '',
            networkId: agent.networkId || '',
            department: agent.department || '',
          });

          setSaveMessage({ type: 'success', text: `Loaded "${agent.name}" for editing` });

          // Clear the editing flag
          localStorage.removeItem('editingAgentId');
        } catch (error) {
          console.error('Failed to load agent for editing:', error);
          setSaveMessage({ type: 'error', text: 'Failed to load agent for editing' });
          localStorage.removeItem('editingAgentId');
        }
      }
    };

    loadAgentForEditing();
  }, []);

  const handleGenerateSchema = async () => {
    if (!agentName.trim() || !wizardData.category) {
      setSchemaError('Please provide an agent name and category first.');
      return;
    }
    setIsGeneratingSchema(true);
    setSchemaError(null);
    try {
      const result = await apiClient.generateSkillSchema({
        name: agentName,
        category: wizardData.category,
        taskDefinition: wizardData.taskDefinition,
        requiredExpertise: wizardData.requiredExpertise,
        decisionAuthority: wizardData.decisionAuthority,
      });
      if (result.success && result.tool_schema) {
        setToolSchema(result.tool_schema as SkillSchema);
        setShowSkillSchema(true);
      } else {
        setSchemaError(result.error || 'Schema generation failed.');
      }
    } catch (err: any) {
      setSchemaError(err.message || 'Failed to generate schema.');
    } finally {
      setIsGeneratingSchema(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!agentName.trim() || !wizardData.category) {
      setSaveMessage({ type: 'error', text: 'Please provide at least an agent name and category.' });
      return;
    }

    setIsSaving(true);
    setSaveMessage(null);

    try {
      const agentData = {
        name: agentName,
        description: wizardData.taskDefinition || 'Custom AI Assistant',
        systemPrompt: systemPrompt,
        category: wizardData.category,
        defaultProvider: 'MAHER AI Engine',
        displayProviderName: 'Powered by MAHER AI',
        status: 'draft' as const,
        toolSchema: toolSchema || undefined,
        implementationType: 'llm_agent' as const,
        skillVersion: '1.0.0',
      };

      if (savedAgentId) {
        // Update existing agent
        const response = await apiClient.updateAgent(savedAgentId, agentData);
        setSaveMessage({ type: 'success', text: `Agent "${agentName}" updated as draft!` });
      } else {
        // Create new agent
        const response = await apiClient.createAgent(agentData);
        setSavedAgentId(response.agent.id);
        setSaveMessage({ type: 'success', text: `Agent "${agentName}" saved as draft!` });
      }
    } catch (error: any) {
      console.error('Save draft error:', error);
      setSaveMessage({ type: 'error', text: error.message || 'Failed to save agent. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!agentName.trim() || !wizardData.category) {
      setSaveMessage({ type: 'error', text: 'Please provide at least an agent name and category.' });
      return;
    }

    setIsSaving(true);
    setSaveMessage(null);

    try {
      const agentData = {
        name: agentName,
        description: wizardData.taskDefinition || 'Custom AI Assistant',
        systemPrompt: systemPrompt,
        category: wizardData.category,
        defaultProvider: 'MAHER AI Engine',
        displayProviderName: 'Powered by MAHER AI',
        status: 'published' as const,
        toolSchema: toolSchema || undefined,
        implementationType: 'llm_agent' as const,
        skillVersion: '1.0.0',
      };

      if (savedAgentId) {
        // Update and publish existing agent
        await apiClient.updateAgent(savedAgentId, agentData);
        await apiClient.publishAgent(savedAgentId);
        setSaveMessage({ type: 'success', text: `Agent "${agentName}" published${toolSchema ? ' as a skill' : ''}! It's now live in the Toolroom.` });
      } else {
        // Create and publish new agent
        const response = await apiClient.createAgent(agentData);
        setSavedAgentId(response.agent.id);
        setSaveMessage({ type: 'success', text: `Agent "${agentName}" created and published${toolSchema ? ' as a skill' : ''}! Check the Toolroom to see it live.` });
      }
    } catch (error: any) {
      console.error('Publish error:', error);
      setSaveMessage({ type: 'error', text: error.message || 'Failed to publish agent. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row h-full text-white bg-brand-deep-blue">
      {/* Configuration Panel */}
      <div className="w-full md:w-1/2 lg:w-2/5 p-6 border-r border-brand-light-blue/20 overflow-y-auto">
        <h2 className="text-2xl font-bold mb-2">Agent Studio</h2>
        <p className="text-sm text-brand-gray mb-6">
          Guide your new AI assistant through its creation, step-by-step.
        </p>

        <div className="space-y-4">
          <div>
            <label htmlFor="agentName" className="block text-sm font-medium text-brand-light-gray mb-1">Agent Name</label>
            <input
              type="text"
              id="agentName"
              value={agentName}
              onChange={(e) => setAgentName(e.target.value)}
              className="w-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
            />
          </div>

          <AgentBuilderWizard
            wizardData={wizardData}
            setWizardData={setWizardData}
          />

          <div className="border-t border-brand-light-blue/20 pt-4">
            <button
              onClick={() => setShowAssembledPrompt(!showAssembledPrompt)}
              className="text-sm text-brand-accent-orange hover:underline"
            >
              {showAssembledPrompt ? 'Hide' : 'View'} Assembled System Prompt
            </button>
            {showAssembledPrompt && (
              <div className="mt-2 p-3 bg-brand-blue rounded-lg border border-brand-light-blue/30 text-xs text-brand-gray whitespace-pre-wrap max-h-60 overflow-y-auto">
                {systemPrompt}
              </div>
            )}
          </div>

          {/* Skill Schema Section */}
          <div className="border-t border-brand-light-blue/20 pt-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-sm font-semibold text-white">Skill Schema</span>
                {toolSchema && (
                  <span className="ml-2 px-2 py-0.5 text-xs bg-green-500/20 text-green-400 border border-green-500/40 rounded-full">
                    Generated
                  </span>
                )}
              </div>
              <button
                onClick={handleGenerateSchema}
                disabled={isGeneratingSchema}
                className="px-3 py-1.5 text-xs bg-brand-light-blue/20 border border-brand-light-blue/40 text-brand-light-gray rounded-lg hover:bg-brand-light-blue/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
              >
                {isGeneratingSchema ? (
                  <>
                    <svg className="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    {toolSchema ? 'Regenerate Schema' : 'Generate Skill Schema'}
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-brand-gray mb-2">
              Generate an OpenAI function-calling schema to make this agent callable as a skill by the orchestrator.
            </p>
            {schemaError && (
              <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded p-2 mb-2">
                {schemaError}
              </div>
            )}
            {toolSchema && (
              <>
                <button
                  onClick={() => setShowSkillSchema(!showSkillSchema)}
                  className="text-xs text-brand-accent-orange hover:underline"
                >
                  {showSkillSchema ? 'Hide' : 'View'} Skill Schema
                </button>
                {showSkillSchema && (
                  <div className="mt-2 p-3 bg-brand-blue rounded-lg border border-green-500/20 text-xs font-mono text-green-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
                    {JSON.stringify(toolSchema, null, 2)}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Save Message */}
          {saveMessage && (
            <div className={`mt-4 p-3 rounded-lg ${saveMessage.type === 'success'
              ? 'bg-green-500/20 border border-green-500/50 text-green-300'
              : 'bg-red-500/20 border border-red-500/50 text-red-300'
              }`}>
              {saveMessage.text}
            </div>
          )}


          {/* Action Buttons */}
          <div className="flex justify-end pt-4 gap-4">
            {isAdmin ? (
              <>
                <button
                  type="button"
                  onClick={handleSaveDraft}
                  disabled={isSaving}
                  className="px-4 py-2 bg-brand-light-blue/20 text-white font-semibold rounded-lg hover:bg-brand-light-blue/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? 'Saving...' : savedAgentId ? 'Update Draft' : 'Save Draft'}
                </button>
                <button
                  type="button"
                  onClick={handlePublish}
                  disabled={isSaving}
                  className="px-4 py-2 bg-brand-accent-orange text-brand-deep-blue font-semibold rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? 'Publishing...' : 'Save & Deploy'}
                </button>
              </>
            ) : (
              <div className="flex flex-col items-end gap-2 w-full">
                <p className="text-xs text-brand-gray mb-1">
                  * Your agent will be submitted as a draft for admin approval.
                </p>
                <button
                  type="button"
                  onClick={handleSaveDraft}
                  disabled={isSaving}
                  className="px-6 py-2 bg-brand-accent-orange text-brand-deep-blue font-semibold rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? 'Submitting...' : 'Submit Agent Request'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat/Testing Panel */}
      <div className="flex-1 flex flex-col">
        <AgentBuilderChat
          key={systemPrompt} // Re-mount chat when prompt changes
          agentConfig={{
            name: agentName,
            systemPrompt: systemPrompt
          } as Agent}
        />
      </div>
    </div>
  );
};

export default AgentStudio;