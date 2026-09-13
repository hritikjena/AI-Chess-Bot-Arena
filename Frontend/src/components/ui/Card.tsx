import React from 'react';

type CardVariant = 'raised' | 'inset' | 'flat';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'raised',
  padding = 'md',
  className = '',
  ...props
}) => {
  const variantClasses = {
    raised: 'neu-raised rounded-xl',
    inset: 'neu-inset rounded-lg',
    flat: 'bg-arena-surface border border-white/5 rounded-xl',
  };

  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={`${variantClasses[variant]} ${paddingClasses[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
