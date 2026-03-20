import React, { useState } from 'react';
import { AppView, Message } from './types';
import { INITIAL_ASSISTANT_MESSAGE } from './constants';

import Sidebar from './components/Sidebar';
import Landing from './components/Landing';
import Chat from './components/Chat';
import AgentStudio from './components/AgentStudio';
import Toolroom from './components/Toolroom';
import RpaSolutions from './components/RpaSolutions';
import Analytics from './components/Analytics';
import Help from './components/Help';
import History from './components/History';
import AboutMe from './components/AboutMe';
import Header from './components/Header';
import SolutionsOverview from './components/SolutionsOverview';
import { AuthProvider, useAuth } from './components/AuthProvider';
import { AdminLogin } from './components/AdminLogin';
import { AdminDashboard } from './components/AdminDashboard';


function App() {
  const { role, logout } = useAuth();
  const [currentView, setCurrentView] = useState<AppView>(AppView.Home);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isChatActive, setIsChatActive] = useState(false);
  const [history, setHistory] = useState<Message[][]>([]);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const saveCurrentChatToHistory = () => {
    // Only save chats that have more than the initial assistant message.
    if (messages.length > 1) {
      const currentChatString = JSON.stringify(messages);
      const isAlreadySaved = history.some(conv => JSON.stringify(conv) === currentChatString);
      if (!isAlreadySaved) {
        setHistory(prevHistory => [messages, ...prevHistory]);
      }
    }
  };

  const handleStartChat = (firstMessage: string) => {
    setMessages([
      { role: 'assistant', content: INITIAL_ASSISTANT_MESSAGE },
      { role: 'user', content: firstMessage },
    ]);
    setIsChatActive(true);
    setCurrentView(AppView.Home);
  };

  const handleGoHome = () => {
    saveCurrentChatToHistory();
    setMessages([]);
    setIsChatActive(false);
    setCurrentView(AppView.Home);
  };

  const handleNewChat = () => {
    saveCurrentChatToHistory();
    setMessages([{ role: 'assistant', content: INITIAL_ASSISTANT_MESSAGE }]);
    setIsChatActive(true);
    setCurrentView(AppView.Home);
  };

  const handleViewHistoryItem = (conversation: Message[]) => {
    saveCurrentChatToHistory();
    setMessages(conversation);
    setIsChatActive(true);
    setCurrentView(AppView.Home);
  };

  const handleLogout = async () => {
    await logout();
    // Reset view to Home after logout/reset
    setCurrentView(AppView.Home);
    setMessages([]);
    setIsChatActive(false);
  };

  const renderMainContent = () => {
    switch (currentView) {
      case AppView.Home:
        return isChatActive ? (
          <Chat messages={messages} setMessages={setMessages} />
        ) : (
          <Landing onStartChat={handleStartChat} setCurrentView={setCurrentView} />
        );
      case AppView.SolutionsOverview:
        return <SolutionsOverview />;
      case AppView.AgentStudio:
        return <AgentStudio />;
      case AppView.Toolroom:
        return <Toolroom />;
      case AppView.RpaSolutions:
        return <RpaSolutions />;
      case AppView.Analytics:
        return <Analytics />;
      case AppView.Help:
        return <Help />;
      case AppView.History:
        return <History history={history} onViewConversation={handleViewHistoryItem} />;
      case AppView.AdminLogin:
        return <AdminLogin onLoginSuccess={() => setCurrentView(AppView.AdminDashboard)} />;
      case AppView.AdminDashboard:
        return <AdminDashboard />;
      case AppView.AboutMe:
        return <AboutMe onNavigate={setCurrentView} />;
      default:
        // Fallback to home view content
        return isChatActive ? (
          <Chat messages={messages} setMessages={setMessages} />
        ) : (
          <Landing onStartChat={handleStartChat} setCurrentView={setCurrentView} />
        );
    }
  };

  const showSidebar = isChatActive || currentView !== AppView.Home;

  return (
    <div
      className="fixed inset-0 w-full h-full bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: "url('https://images.unsplash.com/photo-1581091226825-a6a2a5a0a4da?q=80&w=2940&auto=format&fit=crop')" }}
    >
      <div className="absolute inset-0 w-full h-full bg-brand-deep-blue/90 backdrop-blur-sm" />
      <div className="relative z-10 flex h-screen font-sans bg-transparent text-white">
        <Sidebar
          isVisible={showSidebar}
          currentView={currentView}
          setCurrentView={setCurrentView}
          onNewChat={handleNewChat}
          onGoHome={handleGoHome}
          onLogout={handleLogout}
          userRole={role}
          isChatActive={isChatActive}
          isCollapsed={isSidebarCollapsed}
          setIsCollapsed={setIsSidebarCollapsed}
        />
        <main className="flex-1 flex flex-col overflow-hidden relative">
          <Header
            onNewChat={handleNewChat}
            setCurrentView={setCurrentView}
            isChatActive={isChatActive}
          />
          <div className="flex-1 overflow-y-auto">
            {renderMainContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;