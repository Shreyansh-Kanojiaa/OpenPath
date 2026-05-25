import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

export interface CardProps extends HTMLMotionProps<"div"> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  interactive?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className = '', padding = 'md', interactive = false, children, ...props }, ref) => {
    
    const paddings = {
      none: "p-0",
      sm: "p-4",
      md: "p-6",
      lg: "p-8",
    };

    const classes = [
      "bg-surface border border-border rounded-xl",
      paddings[padding],
      className
    ].filter(Boolean).join(" ");

    return (
      <motion.div
        ref={ref}
        className={classes}
        whileHover={interactive ? { y: -4, boxShadow: '0 0 20px rgba(122, 162, 247, 0.15)' } : {}}
        transition={{ duration: 0.2, ease: "easeOut" }}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

Card.displayName = 'Card';
