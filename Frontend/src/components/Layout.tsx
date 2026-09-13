import React from 'react';
import { Bot, Swords, Trophy, Activity } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  
  const mainNavItems = [
    { name: 'Dashboard', path: '/dashboard', icon: Activity },
    { name: 'Bots', path: '/', icon: Bot },
    { name: 'Match', path: '/match', icon: Swords },
    { name: 'Tournaments', path: '/tournaments', icon: Trophy },
  ];

  return (
    <div className="flex h-screen bg-arena-bg text-arena-primary font-sans">
      <aside className="w-64 bg-arena-surface border-r border-arena flex flex-col shadow-2xl relative z-10">
        <div className="p-8 pb-4">
          <h1 className="text-2xl font-display font-semibold tracking-widest text-arena-primary uppercase">
            Chess Bot<br/>
            <span className="text-arena-accent">Arena</span>
          </h1>
          <p className="text-[10px] uppercase tracking-widest text-arena-muted mt-2 font-mono">
            Intelligence Platform
          </p>
        </div>
        
        <nav className="flex-1 px-4 py-8 space-y-2">
          {mainNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive 
                    ? 'neu-inset text-arena-accent font-medium' 
                    : 'text-arena-secondary hover:text-arena-primary hover:bg-white/5'
                }`}
              >
                <Icon size={18} strokeWidth={isActive ? 2.5 : 1.5} />
                <span className="text-sm tracking-wide">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      
      <main className="flex-1 overflow-auto bg-arena-bg relative">
        <div className="max-w-7xl mx-auto p-8 md:p-12">
          {children}
        </div>
      </main>
    </div>
  );
}
