import React from 'react';
import { motion } from 'framer-motion';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', iconLeft, iconRight, fullWidth, children, disabled, ...props }, ref) => {
    
    const baseStyles = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50";
    
    const variants = {
      primary: "bg-primary text-background hover:bg-primaryHover hover:shadow-[0_0_15px_rgba(122,162,247,0.3)] border border-transparent",
      secondary: "bg-transparent border border-border text-text hover:bg-surfaceHover",
    };
    
    const sizes = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-base",
      lg: "px-6 py-3 text-lg",
    };

    const classes = [
      baseStyles,
      variants[variant],
      sizes[size],
      fullWidth ? "w-full" : "",
      disabled ? "opacity-50 cursor-not-allowed" : "",
      className
    ].filter(Boolean).join(" ");

    return (
      <motion.button
        ref={ref}
        className={classes}
        disabled={disabled}
        whileHover={!disabled ? { scale: 1.02 } : {}}
        whileTap={!disabled ? { scale: 0.98 } : {}}
        {...props}
      >
        {iconLeft && <span className="mr-2 flex items-center">{iconLeft}</span>}
        {children}
        {iconRight && <span className="ml-2 flex items-center">{iconRight}</span>}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';
