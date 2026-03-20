import React, { useState, useEffect } from 'react';
import { WizardData } from '../types';
import { WIZARD_STEPS } from '../constants';
import KnowledgeUpload from './KnowledgeUpload';

interface AgentBuilderWizardProps {
  wizardData: WizardData;
  setWizardData: React.Dispatch<React.SetStateAction<WizardData>>;
}

const AgentBuilderWizard: React.FC<AgentBuilderWizardProps> = ({ wizardData, setWizardData }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [agentId, setAgentId] = useState<string>('');
  const totalSteps = WIZARD_STEPS.length;
  const isCompletionStep = currentStep === totalSteps;

  // Generate a unique agent ID for this wizard session
  useEffect(() => {
    const id = `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setAgentId(id);
  }, []);

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setWizardData(prev => ({ ...prev, [name]: value }));
  };

  const step = WIZARD_STEPS[currentStep];

  return (
    <div className="bg-brand-blue/50 p-4 rounded-lg border border-brand-light-blue/20 min-h-[350px] flex flex-col">
      {isCompletionStep ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center">
          <svg className="w-16 h-16 text-brand-accent-green mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          <h3 className="font-semibold text-lg text-white">Configuration Complete!</h3>
          <p className="text-sm text-brand-gray mt-2">
            Your agent is now ready for testing in the panel on the right.
          </p>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">{step.title}</h3>
            <span className="text-sm text-brand-gray">{currentStep + 1} / {totalSteps}</span>
          </div>

          <p className="text-sm text-brand-gray mb-3">{step.question}</p>

          <div className="flex-1 overflow-y-auto">
            {step.id === 'category' ? (
              <select
                name="category"
                id="category"
                value={wizardData.category}
                onChange={handleChange}
                className="w-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
              >
                <option value="">Select a domain...</option>
                <option value="maintenance">Maintenance</option>
                <option value="operations">Operations</option>
                <option value="finance">Finance</option>
                <option value="other">Other</option>
              </select>
            ) : (step as any).type === 'knowledge' ? (
              agentId && (
                <KnowledgeUpload
                  agentId={agentId}
                  onKnowledgeUpdated={() => {
                    console.log('Knowledge updated for agent:', agentId);
                  }}
                />
              )
            ) : (step as any).type === 'authorInfo' ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-brand-gray mb-1">Network ID</label>
                  <input
                    type="text"
                    name="networkId"
                    value={wizardData.networkId || ''}
                    onChange={(e: any) => handleChange(e as any)}
                    className="w-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
                    placeholder="e.g., AZ12345"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-brand-gray mb-1">Department Name</label>
                  <input
                    type="text"
                    name="department"
                    value={wizardData.department || ''}
                    onChange={(e: any) => handleChange(e as any)}
                    className="w-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
                    placeholder="e.g., Maintenance Planning"
                  />
                </div>
              </div>
            ) : (
              <textarea
                id={step.id}
                name={step.id}
                rows={5}
                value={wizardData[step.id as keyof Omit<WizardData, 'category'>]}
                onChange={handleChange}
                className="w-full h-full p-2 bg-brand-blue border border-brand-light-blue/30 rounded-lg text-white resize-none focus:outline-none focus:ring-2 focus:ring-brand-accent-orange"
                placeholder={step.placeholder}
              />
            )}
          </div>
        </>
      )}

      <div className="flex justify-between items-center mt-4">
        <button
          onClick={handlePrev}
          disabled={currentStep === 0}
          className="px-4 py-2 text-sm font-medium text-brand-light-gray rounded-lg hover:bg-brand-light-blue/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        {!isCompletionStep && (
          <button
            onClick={handleNext}
            className="px-4 py-2 text-sm font-medium bg-brand-light-blue/30 text-white rounded-lg hover:bg-brand-light-blue/50"
          >
            {currentStep === totalSteps - 1 ? 'Finish' : 'Next'}
          </button>
        )}
      </div>
    </div>
  );
};

export default AgentBuilderWizard;
