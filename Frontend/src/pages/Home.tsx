import { useEffect, useState } from 'react';
import { Upload, Play, Cpu, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { BentoGrid } from '../components/bento/BentoGrid';
import { BentoCard } from '../components/bento/BentoCard';
import { Button } from '../components/ui/Button';

interface BotData {
  id: number;
  name: string;
  filename: string;
  description: string;
}

export default function Home() {
  const [bots, setBots] = useState<BotData[]>([]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL}/bots/`)
      .then(res => res.json())
      .then(data => setBots(data))
      .catch(err => console.error("Failed to fetch bots:", err));
  }, []);

  return (
    <div className="space-y-12 animate-in fade-in duration-500">
      
      {/* Premium Hero Section */}
      <section className="neu-inset rounded-2xl p-10 lg:p-14 border border-arena relative overflow-hidden flex flex-col justify-between">
        <div className="relative z-10 max-w-3xl space-y-6">
          <p className="text-arena-accent uppercase tracking-widest text-xs font-mono font-semibold">
            Autonomous Engine Laboratory
          </p>
          <h1 className="text-5xl lg:text-6xl font-display font-medium text-arena-primary leading-tight">
            Design. Compete.<br />
            <span className="text-arena-secondary italic">Analyze Intelligently.</span>
          </h1>
          <p className="text-lg text-arena-muted max-w-xl font-light">
            Upload your autonomous chess engine and pit it against the world. Discover tactical brilliance and brutal blunders in a fully automated, AI-analyzed arena.
          </p>
          <div className="flex gap-4 pt-6">
            <Button size="lg" className="flex items-center gap-2">
              <Upload size={18} />
              Deploy Engine
            </Button>
            <Link to="/match">
              <Button variant="secondary" size="lg" className="flex items-center gap-2">
                <Play size={18} />
                Observe Matches
              </Button>
            </Link>
          </div>
        </div>
        
        {/* Subtle decorative elements */}
        <div className="absolute -right-20 -bottom-20 opacity-5 pointer-events-none text-arena-accent">
          <Cpu size={400} strokeWidth={0.5} />
        </div>
      </section>

      {/* Bots Grid */}
      <section className="space-y-8">
        <div className="flex items-center justify-between border-b border-arena pb-4">
          <h2 className="text-3xl font-display font-medium text-arena-primary tracking-wide flex items-center gap-3">
            <Sparkles className="text-arena-accent" size={24} />
            Registered Engines
          </h2>
          <span className="text-arena-muted font-mono text-sm tracking-widest uppercase">
            {bots.length} Active
          </span>
        </div>
        
        <BentoGrid columns={3}>
          {bots.map((bot, index) => {
            // Create a pseudo-random stable visual identity based on index
            const accentColors = ['text-arena-accent', 'text-success', 'text-arena-primary'];
            const colorClass = accentColors[index % accentColors.length];

            return (
              <BentoCard key={bot.id} noPadding className="group hover:-translate-y-1 transition-transform duration-300">
                <div className="p-6 border-b border-arena/50 flex justify-between items-start bg-white/[0.02]">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-widest text-arena-muted mb-1 block">
                      Engine 0{bot.id}
                    </span>
                    <h3 className={`text-2xl font-display font-semibold ${colorClass} truncate`}>
                      {bot.name}
                    </h3>
                  </div>
                  <div className="neu-inset p-3 rounded-lg text-arena-muted group-hover:text-arena-primary transition-colors">
                    <Cpu size={20} strokeWidth={1.5} />
                  </div>
                </div>
                
                <div className="p-6 flex-1 flex flex-col justify-between">
                  <p className="text-sm text-arena-secondary font-light line-clamp-3 mb-6">
                    {bot.description || 'An autonomous chess engine developed for the arena.'}
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="neu-inset p-3 rounded-lg flex flex-col items-center justify-center">
                      <span className="text-xs font-mono text-arena-muted uppercase tracking-wider mb-1">Win Rate</span>
                      <span className="text-lg font-semibold text-arena-primary">--%</span>
                    </div>
                    <div className="neu-inset p-3 rounded-lg flex flex-col items-center justify-center">
                      <span className="text-xs font-mono text-arena-muted uppercase tracking-wider mb-1">Matches</span>
                      <span className="text-lg font-semibold text-arena-primary">0</span>
                    </div>
                  </div>
                </div>
              </BentoCard>
            );
          })}
        </BentoGrid>
      </section>
      
    </div>
  );
}
