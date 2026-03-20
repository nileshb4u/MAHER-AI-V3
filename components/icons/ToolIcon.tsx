
import React from 'react';

const ToolIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.878-5.878m0 0L11.42 15.17m5.878-5.878L15.17 11.42m-2.929 2.929-2.929-2.929m0 0L3 21m12.121-12.121a3 3 0 0 0-4.242 0L4.16 12.682a3 3 0 0 0 0 4.243l2.121 2.121a3 3 0 0 0 4.243 0l5.656-5.657a3 3 0 0 0 0-4.242Z" />
  </svg>
);

export default ToolIcon;
