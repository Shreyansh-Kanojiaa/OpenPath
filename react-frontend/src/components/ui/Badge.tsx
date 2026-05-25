import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'warning' | 'success' | 'error' | 'outline';
}

export const Badge: React.FC<BadgeProps> = ({ 
  className = '', 
  variant = 'primary', 
  children, 
  ...props 
}) => {
  const variants = {
    primary: "bg-primary bg-opacity-20 text-primary border border-primary border-opacity-20",
    secondary: "bg-surfaceHover text-textMuted border border-border",
    accent: "bg-accent bg-opacity-20 text-accent border border-accent border-opacity-30",
    warning: "bg-warning bg-opacity-20 text-warning border border-warning border-opacity-20",
    success: "bg-success bg-opacity-20 text-success border border-success border-opacity-20",
    error: "bg-error bg-opacity-20 text-error border border-error border-opacity-20",
    outline: "bg-transparent text-textLight border border-border",
  };

  return (
    <span 
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
