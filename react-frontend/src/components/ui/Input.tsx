import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', label, error, ...props }, ref) => {
    
    return (
      <div className="w-full">
        {label && (
          <label className="text-sm text-textMuted mb-1 block font-medium">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`w-full bg-surface border border-border rounded-lg px-4 py-2 text-text placeholder:text-textLight focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary focus:ring-opacity-20 transition-all ${
            error ? 'border-error focus:border-error focus:ring-error focus:ring-opacity-20' : ''
          } ${className}`}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-error">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
