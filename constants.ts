

import { AppView, Agent, AgentTask } from './types';
import SolutionsOverviewIcon from './components/icons/SolutionsOverviewIcon';
import AgentIcon from './components/icons/AgentIcon';
import ToolIcon from './components/icons/ToolIcon';

export const INITIAL_ASSISTANT_MESSAGE = "Hello! I'm MAHER AI, your Virtual Maintenance Assistant. How can I help you today?";

export const SIMULATED_AGENT_TASKS: Omit<AgentTask, 'status'>[] = [
  { id: '1', label: 'Deconstructing Query' },
  { id: '2', label: 'Retrieving Data' },
  { id: '3', label: 'Synthesizing Information' },
  { id: '4', label: 'Generating Response' },
  { id: '5', label: 'Finalizing' },
];

export const LANDING_TILES = [
  {
    name: AppView.SolutionsOverview,
    icon: SolutionsOverviewIcon,
    description: 'Explore pre-built AI assistants and automated workflows.',
  },
  {
    name: AppView.AgentStudio,
    icon: AgentIcon,
    description: 'Design, test, and deploy your own custom AI agents.',
  },
  {
    name: AppView.Toolroom,
    icon: ToolIcon,
    description: 'Browse and launch specialized AI assistants for any task.',
  },
];

export const SUGGESTED_QUESTIONS = [
  "What is the maintenance schedule for Pump-12B?",
  "Generate a safety checklist for confined space entry.",
  "Summarize the last incident report regarding the compressor unit.",
];

export const AGENTS_DATA: Agent[] = [
  {
    id: 'agent-1',
    name: 'Schematic Analyst',
    description: 'Interprets and answers questions about technical drawings, P&IDs, and electrical diagrams. Upload a file to get started.',
    systemPrompt: 'You are an expert in interpreting technical schematics, P&IDs, and electrical diagrams. When a user uploads a schematic and asks a question, analyze the visual information to provide a precise and accurate answer. Identify components, trace circuits/pipelines, and explain relationships as requested.',
    category: 'maintenance',
    statusText: 'Available',
    statusClass: 'available',
    iconSVG: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" /></svg>',
    iconBackgroundColor: '#2563eb',
    defaultProvider: 'MAHER AI Engine',
    displayProviderName: 'Powered by MAHER AI',
    implementationType: 'llm_agent',
    skillVersion: '1.0.0',
    isSkill: true,
    toolSchema: {
      type: 'function',
      function: {
        name: 'schematic_analyst',
        description: 'Analyze technical schematics, P&IDs, and electrical diagrams to answer maintenance engineering questions about components, circuits, and pipelines.',
        parameters: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'The specific question about the schematic or diagram' },
            diagram_type: { type: 'string', description: 'Type of diagram: P&ID, electrical, mechanical, or general', enum: ['P&ID', 'electrical', 'mechanical', 'general'] },
            component_id: { type: 'string', description: 'Specific component tag or ID to focus on (optional)' },
          },
          required: ['query'],
        },
      },
    },
  },
  {
    id: 'agent-2',
    name: 'Procedure Writer',
    description: 'Generates step-by-step Standard Operating Procedures (SOPs) or maintenance routines based on your requirements.',
    systemPrompt: 'You are a technical writer specializing in creating Standard Operating Procedures (SOPs) for industrial maintenance. Based on the user\'s request, generate a clear, concise, and safe step-by-step procedure. Always include a list of required tools, necessary PPE, and explicit safety warnings before the main steps.',
    category: 'maintenance',
    statusText: 'Available',
    statusClass: 'available',
    iconSVG: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>',
    iconBackgroundColor: '#db2777',
    defaultProvider: 'MAHER AI Engine',
    displayProviderName: 'Powered by MAHER AI',
    implementationType: 'llm_agent',
    skillVersion: '1.0.0',
    isSkill: true,
    toolSchema: {
      type: 'function',
      function: {
        name: 'procedure_writer',
        description: 'Generate step-by-step Standard Operating Procedures (SOPs) and maintenance routines for industrial equipment tasks including required tools, PPE, and safety warnings.',
        parameters: {
          type: 'object',
          properties: {
            task_description: { type: 'string', description: 'Description of the maintenance task or procedure to write' },
            equipment_type: { type: 'string', description: 'Type of equipment (e.g., pump, compressor, valve, heat exchanger)' },
            skill_level: { type: 'string', description: 'Target audience skill level', enum: ['trainee', 'technician', 'engineer'] },
            include_loto: { type: 'boolean', description: 'Whether to include Lock-Out/Tag-Out (LOTO) steps' },
          },
          required: ['task_description'],
        },
      },
    },
  },
  {
    id: 'agent-3',
    name: 'Incident Report Analyzer',
    description: 'Summarizes incident reports, identifies root causes, and suggests corrective actions to prevent recurrence.',
    systemPrompt: 'You are an AI assistant for safety officers and reliability engineers. Your task is to analyze incident reports. When a user provides a report, summarize the key events, identify the likely root cause(s) using methodologies like 5-Whys, and propose concrete, actionable corrective and preventive actions (CAPAs).',
    category: 'safety',
    statusText: 'In Development',
    statusClass: 'development',
    iconSVG: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>',
    iconBackgroundColor: '#ca8a04',
    defaultProvider: 'MAHER AI Engine',
    displayProviderName: 'Powered by MAHER AI',
    implementationType: 'llm_agent',
    skillVersion: '1.0.0',
    isSkill: true,
    toolSchema: {
      type: 'function',
      function: {
        name: 'incident_report_analyzer',
        description: 'Analyze safety incident reports to identify root causes using 5-Whys methodology and generate corrective and preventive actions (CAPAs) for industrial safety management.',
        parameters: {
          type: 'object',
          properties: {
            incident_text: { type: 'string', description: 'Full text of the incident report to analyze' },
            analysis_depth: { type: 'string', description: 'Depth of root cause analysis', enum: ['summary', 'standard', 'detailed'] },
            focus_area: { type: 'string', description: 'Specific aspect to focus on: equipment, human_factors, procedures, or environment' },
          },
          required: ['incident_text'],
        },
      },
    },
  },
  {
    id: 'agent-4',
    name: 'Contracts Assistant',
    description: 'Reviews commercial contracts, highlights key clauses, identifies risks, and answers questions about terms and conditions.',
    systemPrompt: 'You are a commercial contract analysis assistant. Your function is to review legal and commercial documents provided by the user. Identify and summarize key clauses such as liability, indemnity, termination, and payment terms. Highlight potential risks or ambiguous language. You are not a lawyer and must include a disclaimer that your analysis is not legal advice.',
    category: 'contracts',
    statusText: 'POC',
    statusClass: 'poc',
    iconSVG: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>',
    iconBackgroundColor: '#4f46e5',
    defaultProvider: 'MAHER AI Engine',
    displayProviderName: 'Powered by MAHER AI',
    implementationType: 'llm_agent',
    skillVersion: '1.0.0',
    isSkill: true,
    toolSchema: {
      type: 'function',
      function: {
        name: 'contracts_assistant',
        description: 'Review commercial contracts to highlight key clauses (liability, indemnity, termination, payment), identify risks, and answer questions about contract terms and conditions.',
        parameters: {
          type: 'object',
          properties: {
            contract_text: { type: 'string', description: 'The contract or clause text to review' },
            analysis_type: { type: 'string', description: 'Type of analysis to perform', enum: ['full_review', 'risk_assessment', 'clause_summary', 'specific_query'] },
            specific_question: { type: 'string', description: 'Specific question about the contract (optional)' },
          },
          required: ['contract_text', 'analysis_type'],
        },
      },
    },
  },
  {
    id: 'agent-5',
    name: 'Operations Copilot',
    description: 'Provides real-time support for plant operators, helping troubleshoot alarms and optimize process parameters.',
    systemPrompt: 'You are an operations support copilot for industrial plant operators. You have access to a knowledge base of operational manuals and historical data. When an operator describes an alarm or a process deviation, provide clear, prioritized troubleshooting steps. Suggest potential adjustments to process parameters to restore stability and efficiency. Always prioritize safety.',
    category: 'operations',
    statusText: 'Available',
    statusClass: 'available',
    iconSVG: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 100 15 7.5 7.5 0 000-15zM21 21l-5.25-5.25" /></svg>',
    iconBackgroundColor: '#059669',
    defaultProvider: 'MAHER AI Engine',
    displayProviderName: 'Powered by MAHER AI',
    implementationType: 'llm_agent',
    skillVersion: '1.0.0',
    isSkill: true,
    toolSchema: {
      type: 'function',
      function: {
        name: 'operations_copilot',
        description: 'Troubleshoot plant alarms and process deviations for industrial operations, providing prioritized steps to restore process stability while maintaining safety.',
        parameters: {
          type: 'object',
          properties: {
            alarm_description: { type: 'string', description: 'Description of the alarm or process deviation observed' },
            unit_name: { type: 'string', description: 'Name or ID of the process unit or equipment involved' },
            current_parameters: { type: 'string', description: 'Current process parameter readings (optional)' },
            urgency: { type: 'string', description: 'Urgency level of the situation', enum: ['low', 'medium', 'high', 'critical'] },
          },
          required: ['alarm_description'],
        },
      },
    },
  },
  {
    id: 'agent-6',
    name: 'Project Planner',
    description: 'Assists in creating project plans, timelines, and resource allocation schedules for maintenance turnarounds.',
    systemPrompt: 'You are a project management assistant specializing in industrial maintenance turnarounds and shutdowns. Given a scope of work, create a high-level project plan. This should include a work breakdown structure (WBS), a Gantt chart timeline, and a list of required resources (personnel by craft, equipment).',
    category: 'projects',
    statusText: 'In Development',
    statusClass: 'development',
    iconSVG: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0h18M-4.5 12h22.5" /></svg>',
    iconBackgroundColor: '#6d28d9',
    defaultProvider: 'MAHER AI Engine',
    displayProviderName: 'Powered by MAHER AI',
    implementationType: 'llm_agent',
    skillVersion: '1.0.0',
    isSkill: true,
    toolSchema: {
      type: 'function',
      function: {
        name: 'project_planner',
        description: 'Create project plans, WBS, Gantt timelines, and resource allocation schedules for industrial maintenance turnarounds and shutdown projects.',
        parameters: {
          type: 'object',
          properties: {
            scope_of_work: { type: 'string', description: 'Description of the maintenance or project scope' },
            duration_days: { type: 'number', description: 'Expected project duration in days' },
            team_size: { type: 'number', description: 'Available team size (number of personnel)' },
            output_format: { type: 'string', description: 'Desired output format', enum: ['wbs', 'gantt', 'resource_plan', 'full_plan'] },
          },
          required: ['scope_of_work'],
        },
      },
    },
  },
];

export const WIZARD_STEPS = [
  { id: 'category', title: 'Agent Domain', question: 'What is the primary domain of this AI Assistant?' },
  { id: 'taskDefinition', title: 'Task Definition', question: 'What specific job will this assistant perform?', placeholder: "e.g., 'Guide technicians through pump seal replacement', 'Verify compliance of work permits against HSE standards'." },
  { id: 'requiredExpertise', title: 'Required Expertise', question: 'What must the assistant know to do this job well?', placeholder: "List specific procedures (SOPs), standards (APIs), equipment, or safety requirements." },
  { id: 'knowledge', title: 'Knowledge Base / Memory Upload', question: 'Upload documents to give your agent access to specific information. This is optional but highly recommended for specialized knowledge.', placeholder: '', type: 'knowledge' },
  { id: 'decisionAuthority', title: 'Decision Authority', question: 'What are the boundaries of its authority?', placeholder: "What can it recommend directly? When must it escalate to a human? What should it NEVER do?" },
  { id: 'communicationTone', title: 'Communication Tone', question: 'What tone should the assistant use?', placeholder: "e.g., 'Formal and precise', 'Supportive and guiding for junior staff', 'Technically detailed'." },
  { id: 'detailLevel', title: 'Level of Detail', question: 'How should the level of detail in its responses vary?', placeholder: "e.g., 'Concise summaries for experienced users', 'Step-by-step for trainees'." },
  { id: 'safetyDisclaimers', title: 'Safety Disclaimers', question: 'What specific safety warnings must be included with certain advice?', placeholder: "e.g., 'Always wear appropriate PPE as per Site Safety Manual Section 4.2 before this task.'" },
  { id: 'escalationPath', title: 'Escalation Path', question: 'When should it explicitly state to get human help?', placeholder: "e.g., 'When should it state \"Refer to Supervisor/Engineer\" or \"Consult the official documentation [document number]\"?'" },
  { id: 'authorInfo', title: 'Author Information', question: 'Please provide your details for the review process.', type: 'authorInfo' }
];

export const CATEGORY_GUARDRAILS = {
  maintenance: `
---
**MAINTENANCE GUARDRAILS:**
1.  All advice must prioritize personal and equipment safety above all else.
2.  Reference specific Standard Operating Procedures (SOPs) or General Instructions (GIs) where applicable.
3.  Always recommend verifying with the latest approved documentation and site-specific conditions.
4.  For any task involving energy isolation, explicitly state the requirement for a valid Lock-Out/Tag-Out (LOTO) procedure.
5.  If a user's query is ambiguous or lacks critical details, ask clarifying questions before providing a procedure.
6.  Always include a concluding disclaimer: "This information is for guidance only. If in doubt, consult your supervisor or a qualified engineer before proceeding."
---
`,
  operations: `
---
**OPERATIONS GUARDRAILS:**
1.  All recommendations must maintain process stability and operational integrity.
2.  Emphasize adherence to established operating envelopes and parameters.
3.  When suggesting parameter changes, recommend small, incremental adjustments and monitoring the effect.
4.  Never recommend bypassing any safety-critical alarm or interlock.
5.  If a situation could lead to an emergency shutdown or unsafe condition, the primary recommendation must be to follow the official emergency procedure and inform the shift supervisor.
6.  Always include a concluding disclaimer: "This guidance is based on standard operating principles. Always operate within the defined parameters for your unit and consult your shift supervisor for any critical decisions."
---
`,
  finance: `
---
**FINANCE GUARDRAILS:**
1.  This AI assistant does not provide financial advice, investment recommendations, or legal interpretations of financial regulations.
2.  All financial data analysis must be based solely on the information provided by the user.
3.  Do not make predictions or forecasts about financial markets or company performance.
4.  When referencing financial policies or procedures, state that the user should always consult the official, most recent documentation from the finance department.
5.  Always include a concluding disclaimer: "This analysis is for informational purposes only and is not a substitute for professional financial advice. Consult with a qualified financial professional for specific guidance."
---
`,
  other: `
---
**GENERAL GUARDRAILS:**
1.  Prioritize safety and accuracy in all responses.
2.  Do not provide medical, legal, or financial advice.
3.  If you do not know the answer, state that you do not have enough information and recommend consulting a subject matter expert.
4.  Encourage users to verify critical information with official documentation.
---
`
};