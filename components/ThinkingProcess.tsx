import React, { useState } from 'react';

interface ThinkingStep {
  step: string;
  status: 'in_progress' | 'completed' | 'failed';
  description: string;
  timestamp: string;
  result?: any;
  reason?: string;
  execution_strategy?: string;
  failures?: any[];
}

interface ThinkingProcessProps {
  thinkingTrail: ThinkingStep[];
}

const ThinkingProcess: React.FC<ThinkingProcessProps> = ({ thinkingTrail }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!thinkingTrail || thinkingTrail.length === 0) {
    return null;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'in_progress':
        return '⟳';
      case 'failed':
        return '✗';
      default:
        return '•';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'in_progress':
        return 'text-blue-600 animate-spin';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="my-4 border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
      {/* Header - Always Visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <span className="text-lg">🧠</span>
          <span className="font-medium text-gray-700">AI Thinking Process</span>
          <span className="text-sm text-gray-500">
            ({thinkingTrail.filter(s => s.status === 'completed').length}/{thinkingTrail.length} steps)
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="px-4 py-3 border-t border-gray-200 bg-white">
          <div className="space-y-4">
            {thinkingTrail.map((step, index) => (
              <div key={index} className="relative pl-8">
                {/* Timeline Line */}
                {index < thinkingTrail.length - 1 && (
                  <div className="absolute left-3 top-6 bottom-0 w-0.5 bg-gray-200" />
                )}

                {/* Step Icon */}
                <div
                  className={`absolute left-0 top-1 w-6 h-6 rounded-full border-2 border-gray-300 bg-white flex items-center justify-center ${getStatusColor(
                    step.status
                  )}`}
                >
                  <span className="text-sm font-bold">{getStatusIcon(step.status)}</span>
                </div>

                {/* Step Content */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-start justify-between">
                    <h4 className="font-medium text-gray-900">{step.step}</h4>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        step.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : step.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {step.status.replace('_', ' ')}
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 mt-1">{step.description}</p>

                  {/* Result Details */}
                  {step.result && step.status === 'completed' && (
                    <div className="mt-2 text-sm">
                      {/* Task Analysis Results */}
                      {step.step === 'Task Analysis' && step.result.subtasks && (
                        <div className="space-y-2">
                          <p className="text-gray-700">
                            <strong>Identified {step.result.subtasks_identified} subtask(s)</strong>
                          </p>
                          <p className="text-gray-600 italic">{step.result.reasoning}</p>
                          <ul className="list-disc list-inside space-y-1 text-gray-600">
                            {step.result.subtasks.map((subtask: any, idx: number) => (
                              <li key={idx}>
                                {subtask.description}
                                <span className="text-gray-500 text-xs ml-2">
                                  ({subtask.preferred_resource})
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Tool Selection Results */}
                      {step.step === 'Tool Selection' && step.result.matches && (
                        <div className="space-y-2">
                          <p className="text-gray-700">
                            <strong>
                              Matched {step.result.tools_matched} tool(s) out of{' '}
                              {step.result.tools_needed} needed
                            </strong>
                          </p>
                          <div className="space-y-2">
                            {step.result.matches.map((match: any, idx: number) => (
                              <div
                                key={idx}
                                className="bg-white border border-gray-200 rounded p-2"
                              >
                                <div className="flex items-center justify-between">
                                  <span className="font-medium text-gray-800">
                                    {match.selected_tool}
                                  </span>
                                  <span
                                    className={`text-xs px-2 py-1 rounded ${
                                      match.tool_type === 'no_match'
                                        ? 'bg-red-100 text-red-700'
                                        : 'bg-green-100 text-green-700'
                                    }`}
                                  >
                                    {match.tool_type}
                                  </span>
                                </div>
                                <p className="text-xs text-gray-600 mt-1">{match.subtask}</p>
                                <p className="text-xs text-gray-500 italic mt-1">{match.reason}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Execution Results */}
                      {step.step === 'Execution' && step.result.summary && (
                        <div className="space-y-1">
                          <p className="text-gray-700">
                            <strong>
                              {step.result.successful} successful, {step.result.failed} failed
                            </strong>
                          </p>
                          <p className="text-gray-600 italic">{step.result.summary}</p>
                        </div>
                      )}

                      {/* Adaptive Replanning Results */}
                      {step.step === 'Adaptive Replanning' && step.result && (
                        <div className="space-y-1">
                          {typeof step.result === 'object' && step.result.replanning_successful ? (
                            <div className="bg-green-50 border border-green-200 rounded p-2 mt-2">
                              <p className="text-sm text-green-800">
                                <strong>✓ Replanning Successful!</strong>
                              </p>
                              <p className="text-xs text-green-700 mt-1">
                                Revised to {step.result.revised_subtasks} subtask(s), matched{' '}
                                {step.result.tools_matched} tool(s)
                              </p>
                              {step.result.reasoning && (
                                <p className="text-xs text-green-600 italic mt-1">
                                  {step.result.reasoning}
                                </p>
                              )}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-600">{String(step.result)}</p>
                          )}
                        </div>
                      )}

                      {/* AI Fallback Results */}
                      {(step.step === 'AI Fallback' ||
                        step.step === 'AI Fallback (After Tool Failure)') &&
                        typeof step.result === 'string' && (
                          <div className="bg-blue-50 border border-blue-200 rounded p-2 mt-2">
                            <p className="text-sm text-blue-800">
                              <strong>ℹ️ {step.result}</strong>
                            </p>
                            {step.reason && (
                              <p className="text-xs text-blue-600 mt-1">Reason: {step.reason}</p>
                            )}
                          </div>
                        )}
                    </div>
                  )}

                  {/* Failure Details */}
                  {step.failures && step.failures.length > 0 && (
                    <div className="mt-2 bg-red-50 border border-red-200 rounded p-2">
                      <p className="text-sm font-medium text-red-800">Tool Failures:</p>
                      <ul className="text-xs text-red-700 mt-1 space-y-1">
                        {step.failures.map((failure: any, idx: number) => (
                          <li key={idx}>
                            • {failure.resource}: {failure.error}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <p className="text-xs text-gray-400 mt-2">
                    {new Date(step.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ThinkingProcess;
