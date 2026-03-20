import React, { useState, useRef, useEffect } from 'react';
import { AppView } from '../types';
import { LANDING_TILES } from '../constants';

interface RightSidebarProps {
  isChatActive: boolean;
  setCurrentView: (view: AppView) => void;
}

const RightSidebar: React.FC<RightSidebarProps> = ({ isChatActive, setCurrentView }) => {
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

  return (
    <aside className={`transition-all duration-500 ease-in-out bg-brand-deep-blue/30 backdrop-blur-sm border-l border-brand-light-blue/10 flex-shrink-0 overflow-hidden ${isChatActive ? 'w-60' : 'w-0'}`}>
      <div className={`p-4 h-full flex flex-col transition-opacity duration-300 ${isChatActive ? 'opacity-100 delay-300' : 'opacity-0'}`}>
        {/* User Profile */}
        <div className="relative" ref={dropdownRef}>
          <button onClick={() => setDropdownOpen(!dropdownOpen)} className="flex items-center gap-3 w-full p-2 rounded-lg hover:bg-brand-blue/50 transition-colors">
            <img src="https://picsum.photos/seed/user/40/40" alt="User Avatar" className="w-10 h-10 rounded-full" />
            <span className="font-semibold text-white truncate">John Doe</span>
          </button>
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-brand-blue rounded-md shadow-lg py-1 z-20 border border-brand-light-blue/20">
              <a href="#" onClick={(e) => { e.preventDefault(); setCurrentView(AppView.History); setDropdownOpen(false); }} className="block px-4 py-2 text-sm text-brand-light-gray hover:bg-brand-light-blue/20">History</a>
              <a href="#" onClick={(e) => { e.preventDefault(); setCurrentView(AppView.AboutMe); setDropdownOpen(false); }} className="block px-4 py-2 text-sm text-brand-light-gray hover:bg-brand-light-blue/20">About Me</a>
            </div>
          )}
        </div>

        <hr className="my-4 border-brand-light-blue/20" />

        {/* Navigation Tiles */}
        <nav className="flex flex-col gap-2">
          {LANDING_TILES.map((tile) => (
            <button
              key={tile.name}
              onClick={() => setCurrentView(tile.name)}
              className="flex items-center gap-3 p-3 rounded-lg text-left text-base font-medium transition-colors text-brand-gray hover:bg-brand-light-blue/20 hover:text-white"
            >
              <tile.icon className="w-5 h-5 flex-shrink-0 text-brand-light-gray" />
              <span className="text-sm">{tile.name}</span>
            </button>
          ))}
        </nav>
      </div>
    </aside>
  );
};

export default RightSidebar;