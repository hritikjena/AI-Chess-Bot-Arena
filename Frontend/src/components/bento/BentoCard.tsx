import React from 'react';
import { Card } from '../ui/Card';

type ColSpan = 1 | 2 | 3 | 4 | 'full';

interface BentoCardProps extends React.HTMLAttributes<HTMLDivElement> {
  colSpan?: ColSpan;
  title?: string;
  subtitle?: string;
  noPadding?: boolean;
}

export const BentoCard: React.FC<BentoCardProps> = ({
  children,
  colSpan = 1,
  title,
  subtitle,
  noPadding = false,
  className = '',
  ...props
}) => {
  const spanClasses = {
    1: 'col-span-1',
    2: 'col-span-1 md:col-span-2',
    3: 'col-span-1 md:col-span-3',
    4: 'col-span-1 md:col-span-2 lg:col-span-4',
    full: 'col-span-1 md:col-span-full',
  };

  return (
    <Card
      variant="raised"
      padding={noPadding ? 'none' : 'lg'}
      className={`flex flex-col ${spanClasses[colSpan]} ${className}`}
      {...props}
    >
      {(title || subtitle) && (
        <div className={`mb-6 ${noPadding ? 'p-6 pb-0' : ''}`}>
          {title && (
            <h3 className="text-xl font-display font-medium text-arena-primary tracking-wide">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-arena-secondary mt-1">
              {subtitle}
            </p>
          )}
        </div>
      )}
      <div className={`flex-1 flex flex-col ${noPadding && !title ? '' : 'h-full'}`}>
        {children}
      </div>
    </Card>
  );
};
