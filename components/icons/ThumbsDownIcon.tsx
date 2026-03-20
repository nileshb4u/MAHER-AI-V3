import React from 'react';

const ThumbsDownIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className={className}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M17.367 13.5c-.806 0-1.533.446-2.031 1.08a9.04 9.04 0 01-2.861 2.4c-.723.384-1.35.956-1.653 1.715a4.498 4.498 0 00-.322 1.672v.633a.75.75 0 01-.75.75A2.25 2.25 0 017.5 19.5c0-1.152.26-2.243.723-3.218.266-.558-.107-1.282-.725-1.282H4.372c-1.026 0-1.945-.694-2.054-1.715a11.95 11.95 0 01-.068-1.285 11.95 11.95 0 012.649-7.521c.388-.482.987-.729 1.605-.729h3.57c.483 0 .964.078 1.423.23l3.114 1.04a4.5 4.5 0 001.423.23h1.153m-1.867 7.5l1.822-1.822a.75.75 0 000-1.061L15.5 8.818m.367 4.682V6.75a.75.75 0 00-.75-.75h-2.25"
    />
  </svg>
);

export default ThumbsDownIcon;
