import React from 'react';
import { AppView } from '../types';
import HomeIcon from './icons/HomeIcon';
import AgentIcon from './icons/AgentIcon';
import ToolIcon from './icons/ToolIcon';
import AnalyticsIcon from './icons/AnalyticsIcon';
import HelpIcon from './icons/HelpIcon';
import NewChatIcon from './icons/NewChatIcon';
import SolutionsOverviewIcon from './icons/SolutionsOverviewIcon';
import ChevronDoubleLeftIcon from './icons/ChevronDoubleLeftIcon';


interface SidebarProps {
  isVisible: boolean;
  currentView: AppView;
  setCurrentView: (view: AppView) => void;
  onNewChat: () => void;
  onGoHome: () => void;
  onLogout: () => void;
  userRole: 'guest' | 'admin' | null;
  isChatActive: boolean;
  isCollapsed: boolean;
  setIsCollapsed: (isCollapsed: boolean) => void;
}

const navItems = [
  { name: AppView.Home, icon: HomeIcon },
  { name: AppView.SolutionsOverview, icon: SolutionsOverviewIcon },
  { name: AppView.AgentStudio, icon: AgentIcon },
  { name: AppView.Toolroom, icon: ToolIcon },
  { name: AppView.Help, icon: HelpIcon },
];


const Sidebar: React.FC<SidebarProps> = ({ isVisible, currentView, setCurrentView, onNewChat, onGoHome, onLogout, userRole, isChatActive, isCollapsed, setIsCollapsed }) => {
  return (
    <aside className={`transition-all duration-300 ease-in-out bg-brand-blue flex-shrink-0 border-r border-brand-light-blue/20 overflow-hidden ${!isVisible ? 'w-0 p-0 border-r-0' : isCollapsed ? 'w-20 p-3' : 'w-64 p-4'
      }`}>
      <div className={`h-full flex flex-col transition-opacity duration-300 ${isVisible ? 'opacity-100' : 'opacity-0'
        }`}>
        <div className={`flex items-center gap-3 mb-4 transition-all duration-300 ${isCollapsed ? 'justify-center' : 'px-2'}`}>
          <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-brand-accent-orange/50 flex-shrink-0">
            <img src="/images/maher-logo.png" alt="MAHER AI Logo" className="w-full h-full object-cover" />
          </div>
          {!isCollapsed && <h1 className="text-2xl font-bold text-white whitespace-nowrap">MAHER AI</h1>}
        </div>

        <div className="relative group">
          <button
            onClick={onNewChat}
            className={`flex items-center gap-3 w-full px-3 py-2.5 mb-6 rounded-lg text-left text-base font-medium transition-colors bg-brand-light-blue/20 text-white hover:bg-brand-light-blue/30 ${isCollapsed ? 'justify-center' : ''}`}
          >
            <NewChatIcon className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span className="whitespace-nowrap">New Chat</span>}
          </button>
          {isCollapsed && (
            <div className="absolute left-full ml-4 top-1/2 -translate-y-1/2 whitespace-nowrap bg-brand-gray text-white text-xs font-semibold rounded py-1 px-3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              New Chat
            </div>
          )}
        </div>

        <nav className="flex flex-col gap-2">
          {navItems.map((item) => {
            const isHomeActive = currentView === AppView.Home && !isChatActive;
            const isOtherActive = item.name !== AppView.Home && currentView === item.name;
            const isActive = isHomeActive || isOtherActive;

            return (
              <div key={item.name} className="relative group">
                <button
                  onClick={() => {
                    if (item.name === AppView.Home) {
                      onGoHome();
                    } else {
                      setCurrentView(item.name);
                    }
                  }}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-left text-base font-medium transition-colors ${isActive
                    ? 'bg-brand-light-blue/30 text-white'
                    : 'text-brand-gray hover:bg-brand-light-blue/20 hover:text-white'
                    } ${isCollapsed ? 'justify-center' : ''}`}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && <span className="whitespace-nowrap">{item.name}</span>}
                </button>
                {isCollapsed && (
                  <div className="absolute left-full ml-4 top-1/2 -translate-y-1/2 whitespace-nowrap bg-brand-gray text-white text-xs font-semibold rounded py-1 px-3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    {item.name}
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        <div className="mt-auto pt-4 border-t border-brand-light-blue/10 flex flex-col gap-2">
          {/* Logout/Reset Button */}
          <div className="relative group">
            <button
              onClick={onLogout}
              className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-left text-base font-medium transition-colors text-brand-gray hover:bg-red-500/20 hover:text-red-300 ${isCollapsed ? 'justify-center' : ''}`}
              aria-label={userRole === 'admin' ? "Logout" : "Reset Session"}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 flex-shrink-0">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
              </svg>
              {!isCollapsed && <span className="whitespace-nowrap">{userRole === 'admin' ? 'Logout Admin' : 'Reset Session'}</span>}
            </button>
            {isCollapsed && (
              <div className="absolute left-full ml-4 top-1/2 -translate-y-1/2 whitespace-nowrap bg-brand-gray text-white text-xs font-semibold rounded py-1 px-3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                {userRole === 'admin' ? 'Logout' : 'Reset'}
              </div>
            )}
          </div>

          <div className="relative group">
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className={`flex items-center w-full gap-3 px-3 py-2.5 rounded-lg text-brand-gray hover:bg-brand-light-blue/20 hover:text-white transition-colors ${isCollapsed ? 'justify-center' : ''}`}
              aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              <ChevronDoubleLeftIcon className={`w-5 h-5 flex-shrink-0 transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`} />
              {!isCollapsed && <span className="text-sm font-medium whitespace-nowrap">Collapse</span>}
            </button>
            {isCollapsed && (
              <div className="absolute left-full ml-4 top-1/2 -translate-y-1/2 whitespace-nowrap bg-brand-gray text-white text-xs font-semibold rounded py-1 px-3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                {isCollapsed ? 'Expand' : 'Collapse'}
              </div>
            )}
          </div>

          <div className={`text-center text-brand-gray text-xs transition-all duration-300 ${isCollapsed ? 'opacity-0 h-0 invisible' : 'opacity-100 mt-2'}`}>
            <p>&copy; {new Date().getFullYear()} MAHER AI Corp.</p>
            <p>Your Virtual Maintenance Assistant</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
