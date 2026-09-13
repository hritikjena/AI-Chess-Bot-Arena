import React from 'react';

interface BentoGridProps extends React.HTMLAttributes<HTMLDivElement> {
  columns?: 1 | 2 | 3 | 4;
}

export const BentoGrid: React.FC<BentoGridProps> = ({
  children,
  columns = 3,
  className = '',
  ...props
}) => {
  const gridColumns = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div
      className={`grid gap-6 ${gridColumns[columns]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
