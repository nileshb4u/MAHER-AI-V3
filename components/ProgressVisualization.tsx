import React, { useState, useEffect } from 'react';
import { AgentTask, TaskStatus } from '../types';
import { SIMULATED_AGENT_TASKS } from '../constants';

const ProgressVisualization: React.FC = () => {
  const [tasks] = useState<AgentTask[]>(
    SIMULATED_AGENT_TASKS.map(task => ({ ...task, status: TaskStatus.Pending }))
  );
  const [currentTaskIndex, setCurrentTaskIndex] = useState(-1);

  useEffect(() => {
    // Initialize the first task immediately
    setCurrentTaskIndex(0);

    const interval = setInterval(() => {
      setCurrentTaskIndex(prevIndex => {
        const nextIndex = prevIndex + 1;
        if (nextIndex >= tasks.length) {
          clearInterval(interval);
          return prevIndex;
        }
        return nextIndex;
      });
    }, 1500); // 1.5 seconds per task

    return () => clearInterval(interval);
  }, [tasks.length]);

  const progressPercentage = currentTaskIndex >= 0 ? ((currentTaskIndex + 0.5) / tasks.length) * 100 : 0;
  const currentTask = tasks[currentTaskIndex];

  return (
    <div className="absolute bottom-2 left-0 right-0 w-full opacity-80">
        {currentTask && (
            <div 
                className="absolute bottom-full mb-2 transition-all duration-1000 ease-linear"
                style={{ 
                    left: `${progressPercentage}%`, 
                    transform: 'translateX(-50%)',
                    opacity: currentTaskIndex < tasks.length ? 1 : 0 // Fade out on completion
                }}
            >
                <div className="bg-brand-blue/80 backdrop-blur-sm text-brand-light-gray text-xs font-medium px-3 py-1 rounded-full shadow-lg whitespace-nowrap">
                    {currentTask.label}...
                </div>
            </div>
        )}
        
        <div className="relative h-1.5 w-full bg-brand-light-blue/20 rounded-full">
            <div
                className="absolute top-0 left-0 h-full bg-brand-accent-green rounded-full transition-all duration-1000 ease-linear"
                style={{ width: `${progressPercentage}%` }}
            ></div>
            <div 
                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-md transition-all duration-1000 ease-linear"
                style={{ 
                    left: `calc(${progressPercentage}% - 6px)`,
                    opacity: currentTaskIndex < tasks.length ? 1 : 0 // Fade out on completion
                }}
            >
                 <div className="w-full h-full bg-brand-accent-green rounded-full animate-pulse"></div>
            </div>
        </div>
    </div>
  );
};

export default ProgressVisualization;