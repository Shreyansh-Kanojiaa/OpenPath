import React from 'react';

export interface ProgressBarProps {
  value: number; // 0 to 100
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ 
  value, 
  showLabel = false,
  className = '' 
}) => {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={`flex items-center gap-3 w-full ${className}`}>
      <div className="flex-1 bg-surface h-2 rounded-full overflow-hidden">
        <div 
          className="bg-primary h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${clampedValue}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-sm font-medium text-text">
          {Math.round(clampedValue)}%
        </span>
      )}
    </div>
  );
};
