import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="flex flex-col gap-2 w-full">
      {label && (
        <label htmlFor={inputId} className="text-xs font-semibold text-arena-secondary uppercase tracking-wider">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`neu-inset w-full px-4 py-2.5 text-sm text-arena-primary placeholder-arena-muted focus:outline-none focus:ring-1 focus:ring-arena-accent transition-all ${error ? 'ring-1 ring-danger' : ''} ${className}`}
        {...props}
      />
      {error && (
        <span className="text-xs text-danger mt-1">{error}</span>
      )}
    </div>
  );
};
