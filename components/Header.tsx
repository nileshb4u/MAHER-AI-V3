import React, { useState, useRef, useEffect } from 'react';
import { AppView } from '../types';
import { useAuth } from './AuthProvider';
import { apiClient } from '../client';

interface HeaderProps {
  onNewChat: () => void;
  setCurrentView: (view: AppView) => void;
  isChatActive: boolean;
}

const Header: React.FC<HeaderProps> = ({ onNewChat, setCurrentView, isChatActive }) => {
  const { isAdmin, refreshRole, sharekUser } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    try {
      await apiClient.logout();
      refreshRole();
      setDropdownOpen(false);
      window.location.reload();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <header className={`w-full p-4 flex items-center ${isChatActive ? 'justify-between' : 'justify-end'} text-white flex-shrink-0`}>
      {/* Left section - only shown when chat is active */}
      {isChatActive && (
        <div>
          <button onClick={onNewChat} className="flex items-center gap-3" aria-label="Start new chat">
            <div className="w-10 h-10 bg-brand-blue rounded-full flex items-center justify-center border border-brand-light-blue/20">
              <svg className="w-6 h-6 text-brand-accent-orange" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z" />
              </svg>
            </div>
          </button>
        </div>
      )}

      {/* Right section */}
      <div className="flex items-center gap-3">
        {/* Admin Badge */}
        {isAdmin && (
          <div className="flex items-center gap-2 px-3 py-1 bg-brand-accent-orange/20 border border-brand-accent-orange/50 rounded-full">
            <svg className="w-4 h-4 text-brand-accent-orange" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
            <span className="text-xs font-semibold text-brand-accent-orange">Admin</span>
          </div>
        )}

        <div className="relative" ref={dropdownRef}>
          <button onClick={() => setDropdownOpen(!dropdownOpen)} className="flex items-center gap-3 p-1 rounded-full hover:bg-brand-blue/50 transition-colors">
            <img src="https://picsum.photos/seed/user/40/40" alt="User Avatar" className="w-10 h-10 rounded-full" />
            <span className="font-semibold text-white truncate hidden sm:block">{isAdmin ? 'Admin' : (sharekUser ? sharekUser.Title : 'Guest')}</span>
          </button>
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-brand-blue rounded-md shadow-lg py-1 z-20 border border-brand-light-blue/20">
              {isAdmin && (
                <>
                  <a href="#" onClick={(e) => { e.preventDefault(); setCurrentView(AppView.History); setDropdownOpen(false); }} className="block px-4 py-2 text-sm text-brand-light-gray hover:bg-brand-light-blue/20">History</a>
                  <a href="#" onClick={(e) => { e.preventDefault(); setCurrentView(AppView.AboutMe); setDropdownOpen(false); }} className="block px-4 py-2 text-sm text-brand-light-gray hover:bg-brand-light-blue/20">Actions</a>
                  <hr className="my-1 border-brand-light-blue/20" />
                </>
              )}

              {!isAdmin ? (
                <a href="#" onClick={(e) => { e.preventDefault(); setCurrentView(AppView.AdminLogin); setDropdownOpen(false); }} className="block px-4 py-2 text-sm text-brand-accent-orange hover:bg-brand-light-blue/20 font-semibold">🔐 Admin Login</a>
              ) : (
                <>
                  <a href="#" onClick={(e) => { e.preventDefault(); setCurrentView(AppView.AdminDashboard); setDropdownOpen(false); }} className="block px-4 py-2 text-sm text-brand-accent-orange hover:bg-brand-light-blue/20 font-semibold">📊 Dashboard</a>
                  <a href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }} className="block px-4 py-2 text-sm text-red-400 hover:bg-brand-light-blue/20 font-semibold">🚪 Logout</a>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
export default Header;