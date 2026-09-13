import { useState, useEffect } from 'react';
import { Activity, Swords, Trophy, BrainCircuit, ShieldAlert, Cpu } from 'lucide-react';
import { Link } from 'react-router-dom';
import { BentoGrid } from '../components/bento/BentoGrid';
import { BentoCard } from '../components/bento/BentoCard';
import { Badge } from '../components/ui/Badge';

interface BotPerformance {
  bot_id: number;
  bot_name: string;
  games_played: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  avg_eval_loss: number;
  total_blunders: number;
  total_mistakes: number;
}

interface AnalyticsSummary {
  total_bots: number;
  total_games: number;
  total_tournaments: number;
  active_tournaments: number;
}

interface AIInsight {
  match_id: number;
  move_number: number;
  color: string;
  move: string;
  eval_before: number;
  eval_after: number;
  loss: number;
  commentary: string;
  fen: string;
}

interface MatchResponse {
  id: number;
  bot1_id: number;
  bot2_id: number;
  result: string;
  status: string;
}

interface DashboardData {
  summary: AnalyticsSummary;
  bot_performance: BotPerformance[];
  recent_games: MatchResponse[];
  live_games: MatchResponse[];
  ai_insights: AIInsight[];
  grandmaster_summary: string;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL}/analytics/dashboard`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="text-arena-muted flex flex-col items-center gap-4">
          <BrainCircuit className="animate-pulse" size={48} />
          <p className="font-mono text-sm tracking-widest uppercase">Initializing Intelligence...</p>
        </div>
      </div>
    );
  }

  if (!data) return <div className="text-danger">Failed to load dashboard data.</div>;

  return (
    <div className="space-y-12 animate-in fade-in duration-500">
      
      {/* Header */}
      <div>
        <h1 className="text-4xl font-display font-medium text-arena-primary tracking-wide">
          Arena Intelligence
        </h1>
        <p className="text-sm text-arena-secondary mt-2 font-light">
          Live overview of autonomous performance, tournament results, and AI analysis.
        </p>
      </div>

      <BentoGrid columns={4}>
        
        {/* Top Metrics Row */}
        <BentoCard colSpan={1} className="justify-center">
          <div className="flex items-center gap-4">
            <div className="p-3 neu-inset rounded-lg text-arena-accent">
              <Cpu size={24} strokeWidth={1.5} />
            </div>
            <div>
              <div className="text-xs font-mono text-arena-muted uppercase tracking-widest">Total Engines</div>
              <div className="text-3xl font-display font-semibold text-arena-primary">{data.summary.total_bots}</div>
            </div>
          </div>
        </BentoCard>

        <BentoCard colSpan={1} className="justify-center">
          <div className="flex items-center gap-4">
            <div className="p-3 neu-inset rounded-lg text-arena-primary">
              <Swords size={24} strokeWidth={1.5} />
            </div>
            <div>
              <div className="text-xs font-mono text-arena-muted uppercase tracking-widest">Matches</div>
              <div className="text-3xl font-display font-semibold text-arena-primary">{data.summary.total_games}</div>
            </div>
          </div>
        </BentoCard>

        <BentoCard colSpan={1} className="justify-center">
          <div className="flex items-center gap-4">
            <div className="p-3 neu-inset rounded-lg text-arena-secondary">
              <Trophy size={24} strokeWidth={1.5} />
            </div>
            <div>
              <div className="text-xs font-mono text-arena-muted uppercase tracking-widest">Tournaments</div>
              <div className="text-3xl font-display font-semibold text-arena-primary">{data.summary.total_tournaments}</div>
            </div>
          </div>
        </BentoCard>

        <BentoCard colSpan={1} className="justify-center">
          <div className="flex items-center gap-4">
            <div className="p-3 neu-inset rounded-lg text-success">
              <Activity size={24} strokeWidth={1.5} />
            </div>
            <div>
              <div className="text-xs font-mono text-arena-muted uppercase tracking-widest">Active Events</div>
              <div className="text-3xl font-display font-semibold text-arena-primary">{data.summary.active_tournaments}</div>
            </div>
          </div>
        </BentoCard>

        {/* AI Grandmaster Summary - Full Width */}
        <BentoCard colSpan="full" className="relative overflow-hidden group">
          <div className="absolute right-0 top-0 bottom-0 opacity-5 pointer-events-none transition-transform duration-1000 group-hover:scale-110">
            <BrainCircuit size={300} strokeWidth={0.5} className="text-arena-accent" />
          </div>
          <div className="relative z-10 max-w-4xl">
            <h2 className="text-sm font-mono text-arena-accent uppercase tracking-widest mb-4 flex items-center gap-3">
              <BrainCircuit size={16} />
              AI Intelligence Report
            </h2>
            <p className="text-2xl font-display font-medium leading-relaxed text-arena-primary/90">
              "{data.grandmaster_summary}"
            </p>
          </div>
        </BentoCard>

        {/* Engine Performance Leaderboard */}
        <BentoCard 
          colSpan={3} 
          title="Engine Performance Rankings"
          noPadding
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="text-arena-muted text-xs font-mono uppercase tracking-widest border-b border-arena">
                <tr>
                  <th className="px-8 py-4 font-normal">Engine</th>
                  <th className="px-8 py-4 font-normal">Win Rate</th>
                  <th className="px-8 py-4 font-normal">W-L-D</th>
                  <th className="px-8 py-4 font-normal">Errors (Bl/Ms)</th>
                  <th className="px-8 py-4 font-normal">Avg CP Loss</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-arena/50">
                {data.bot_performance.sort((a,b) => b.win_rate - a.win_rate).map((bot, i) => (
                  <tr key={bot.bot_id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="px-8 py-4 font-medium flex items-center gap-4">
                      <span className="text-arena-muted font-mono text-xs w-4">{i + 1}.</span>
                      <span className="text-arena-primary group-hover:text-arena-accent transition-colors">{bot.bot_name}</span>
                    </td>
                    <td className="px-8 py-4">
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-arena-primary min-w-[3rem]">{bot.win_rate.toFixed(1)}%</span>
                        <div className="w-24 h-1 neu-inset rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-arena-accent transition-all duration-1000"
                            style={{ width: `${bot.win_rate}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-4 font-mono text-arena-secondary">
                      <span className="text-success">{bot.wins}</span> -{' '}
                      <span className="text-danger">{bot.losses}</span> -{' '}
                      <span className="text-arena-muted">{bot.draws}</span>
                    </td>
                    <td className="px-8 py-4 font-mono">
                      <span className="text-danger">{bot.total_blunders}</span> / <span className="text-warning">{bot.total_mistakes}</span>
                    </td>
                    <td className="px-8 py-4 font-mono text-arena-secondary">
                      {(bot.avg_eval_loss * 100).toFixed(0)}
                    </td>
                  </tr>
                ))}
                {data.bot_performance.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-8 py-12 text-center text-arena-muted font-light">
                      No matches have been played yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </BentoCard>

        {/* Critical Moments */}
        <BentoCard 
          colSpan={1} 
          title="Critical Moments"
          noPadding
        >
          <div className="divide-y divide-arena/50 overflow-y-auto max-h-[400px]">
            {data.ai_insights.map((insight, i) => (
              <div key={i} className="p-6 hover:bg-white/[0.02] transition-colors">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-sm ${insight.color === 'white' ? 'bg-arena-primary' : 'neu-inset border border-arena'}`} />
                    <span className="font-mono text-xs uppercase tracking-widest text-arena-secondary">Move {insight.move_number}: {insight.move}</span>
                  </div>
                  <Badge variant={insight.loss >= 1.5 ? 'danger' : 'warning'}>
                    {insight.loss >= 1.5 ? 'BLUNDER' : 'MISTAKE'}
                  </Badge>
                </div>
                
                <p className="text-sm text-arena-primary font-light leading-relaxed mb-4">
                  "{insight.commentary}"
                </p>
                
                <div className="flex justify-between items-center text-xs font-mono text-arena-muted">
                  <Link to={`/match?id=${insight.match_id}`} className="hover:text-arena-accent transition-colors">
                    MATCH #{insight.match_id}
                  </Link>
                  <span>
                    EVAL: {insight.eval_before > 0 ? '+' : ''}{insight.eval_before.toFixed(1)} ➔ {insight.eval_after > 0 ? '+' : ''}{insight.eval_after.toFixed(1)}
                  </span>
                </div>
              </div>
            ))}
            
            {data.ai_insights.length === 0 && (
              <div className="p-12 text-center text-arena-muted flex flex-col items-center gap-4">
                <ShieldAlert size={32} strokeWidth={1} className="opacity-50" />
                <p className="font-light text-sm">No critical insights detected yet.</p>
              </div>
            )}
          </div>
        </BentoCard>

      </BentoGrid>
    </div>
  );
}
