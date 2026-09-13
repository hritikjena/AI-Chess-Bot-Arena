import React from 'react';

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'accent';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className = '',
  ...props
}) => {
  const variantClasses = {
    default: 'bg-white/5 text-arena-secondary border border-white/10',
    success: 'bg-success/10 text-success border border-success/20',
    warning: 'bg-warning/10 text-warning border border-warning/20',
    danger: 'bg-danger/10 text-danger border border-danger/20',
    accent: 'bg-arena-accent/10 text-arena-accent border border-arena-accent/20',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono font-medium tracking-wide ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
