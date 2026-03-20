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