import React, { useEffect, useState } from 'react';
import { Upload, Play, Shield, Cpu } from 'lucide-react';
import { Link } from 'react-router-dom';

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
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-900 to-slate-900 border border-slate-800 p-10">
        <div className="relative z-10 max-w-2xl space-y-6">
          <h1 className="text-5xl font-extrabold tracking-tight text-white">
            Build. Battle. <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">Analyze.</span>
          </h1>
          <p className="text-lg text-slate-300">
            Upload your chess bot and watch it compete against other engines. Discover tactical brilliance and brutal blunders in a fully automated arena.
          </p>
          <div className="flex gap-4 pt-4">
            <button className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold transition-all hover:scale-105 active:scale-95 shadow-lg shadow-blue-900/50">
              <Upload size={20} />
              Upload Bot
            </button>
            <Link to="/match" className="flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-semibold transition-all border border-slate-700 hover:border-slate-500 hover:scale-105 active:scale-95">
              <Play size={20} />
              Watch Match
            </Link>
          </div>
        </div>
        
        {/* Abstract Background Design */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-20 pointer-events-none">
          <div className="w-full h-full bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-400 via-transparent to-transparent blur-2xl"></div>
        </div>
      </section>

      {/* Bot Arena Grid */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Shield className="text-amber-500" />
            Arena Competitors
          </h2>
          <span className="text-slate-400 font-medium bg-slate-800 px-3 py-1 rounded-full text-sm">
            {bots.length} Bots Registered
          </span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {bots.map((bot) => (
            <div key={bot.id} className="group bg-slate-800/50 border border-slate-700 hover:border-blue-500/50 rounded-xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-blue-900/20">
              <div className="flex justify-between items-start mb-4">
                <div className="p-3 bg-slate-900/80 rounded-lg text-blue-400 group-hover:text-amber-400 group-hover:bg-slate-900 transition-colors">
                  <Cpu size={24} />
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Win Rate</span>
                  <span className="text-lg font-bold text-slate-200">--%</span>
                </div>
              </div>
              <h3 className="text-xl font-bold text-slate-100 mb-2 truncate">{bot.name}</h3>
              <p className="text-sm text-slate-400 line-clamp-2 min-h-[2.5rem]">{bot.description}</p>
              
              <div className="mt-6 pt-4 border-t border-slate-700/50 flex justify-between items-center text-sm text-slate-400">
                <span>0 matches played</span>
              </div>
            </div>
          ))}
        </div>
      </section>
      
    </div>
  );
}
