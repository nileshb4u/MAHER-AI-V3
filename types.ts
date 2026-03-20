export enum AppView {
  Home = 'Home',
  SolutionsOverview = "What's Cooking",
  AgentStudio = 'Agent Studio',
  Toolroom = 'Toolroom',
  RpaSolutions = 'RPA Solutions',
  Analytics = 'Analytics',
  Help = 'Help',
  History = 'History',
  AboutMe = 'About Me',
  AdminLogin = 'Admin Login',
  AdminDashboard = 'Admin Dashboard',
}

export interface ThinkingStep {
  step: string;
  status: 'in_progress' | 'completed' | 'failed';
  description: string;
  timestamp: string;
  result?: any;
  reason?: string;
  execution_strategy?: string;
  failures?: any[];
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  isThinking?: boolean;
  thinking_process?: ThinkingStep[];
  skillsUsed?: string[];   // skill names invoked by the orchestrator for this message
}

export enum TaskStatus {
  Pending = 'pending',
  InProgress = 'in-progress',
  Completed = 'completed',
}

export interface AgentTask {
  id: string;
  label: string;
  status: TaskStatus;
}

// ── Skill schema types (OpenAI function-calling format) ────────────────────

export interface SkillParameterDef {
  type: 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object';
  description: string;
  enum?: string[];
  items?: { type: string };
}

export interface SkillSchema {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: Record<string, SkillParameterDef>;
      required: string[];
    };
  };
}

// ── Agent / Skill ──────────────────────────────────────────────────────────

export interface Agent {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  category: string;
  statusText: string;
  statusClass: string;
  iconSVG: string;
  iconBackgroundColor: string;
  defaultProvider: string;
  displayProviderName: string;
  networkId?: string;
  department?: string;

  // Skill fields — present when this agent has been promoted to a skill
  toolSchema?: SkillSchema | null;
  implementationType?: 'llm_agent' | 'rag_pipeline' | 'workflow' | 'local_function';
  skillVersion?: string;
  isSkill?: boolean;     // true when toolSchema is present and published
}

export interface WizardData {
  category: 'maintenance' | 'operations' | 'finance' | 'other' | '';
  taskDefinition: string;
  requiredExpertise: string;
  knowledge: string;
  decisionAuthority: string;
  communicationTone: string;
  detailLevel: string;
  safetyDisclaimers: string;
  escalationPath: string;
  networkId: string;
  department: string;
}
