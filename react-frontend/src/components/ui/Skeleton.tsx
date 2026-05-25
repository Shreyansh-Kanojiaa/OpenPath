import React from 'react';

export interface SkeletonProps {
  variant?: 'text' | 'circle' | 'image' | 'card';
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ 
  variant = 'text', 
  className = '' 
}) => {
  const variants = {
    text: "h-4 w-full rounded",
    circle: "rounded-full w-12 h-12",
    image: "w-full h-48 rounded-lg",
    card: "w-full h-32 rounded-xl"
  };

  return (
    <div 
      className={`bg-surface animate-pulse ${variants[variant]} ${className}`}
      aria-hidden="true"
    />
  );
};
