import React, { useState, useEffect } from 'react';
import { Activity, Users, Swords, Trophy, TrendingUp, AlertTriangle, BrainCircuit, XCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

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
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!data) return <div className="text-white">Failed to load dashboard</div>;

  return (
    <div className="space-y-6 text-slate-100">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-amber-500 flex items-center gap-3">
          <Activity size={32} className="text-blue-500" />
          Intelligence Center
        </h1>
      </div>

      {/* AI Summary Banner */}
      <div className="bg-gradient-to-r from-slate-800 to-indigo-900 border border-indigo-500/30 rounded-xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <BrainCircuit size={120} />
        </div>
        <div className="relative z-10">
          <h2 className="text-lg font-semibold text-indigo-300 flex items-center gap-2 mb-2">
            <BrainCircuit size={20} />
            Grandmaster AI Analysis
          </h2>
          <p className="text-xl font-medium leading-relaxed">
            {data.grandmaster_summary}
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg">
            <Users size={24} />
          </div>
          <div>
            <div className="text-slate-400 text-sm font-medium">Total Bots</div>
            <div className="text-2xl font-bold">{data.summary.total_bots}</div>
          </div>
        </div>
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg">
            <Swords size={24} />
          </div>
          <div>
            <div className="text-slate-400 text-sm font-medium">Games Played</div>
            <div className="text-2xl font-bold">{data.summary.total_games}</div>
          </div>
        </div>
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <Trophy size={24} />
          </div>
          <div>
            <div className="text-slate-400 text-sm font-medium">Tournaments</div>
            <div className="text-2xl font-bold">{data.summary.total_tournaments}</div>
          </div>
        </div>
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 text-purple-400 rounded-lg">
            <Activity size={24} />
          </div>
          <div>
            <div className="text-slate-400 text-sm font-medium">Active Events</div>
            <div className="text-2xl font-bold">{data.summary.active_tournaments}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leaderboard */}
        <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-xl overflow-hidden flex flex-col h-[500px]">
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <TrendingUp size={20} className="text-blue-400" />
              Bot Performance Leaderboard
            </h2>
          </div>
          <div className="overflow-auto flex-1 p-0 m-0">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-700/50 text-slate-400 sticky top-0">
                <tr>
                  <th className="px-4 py-3 font-medium">Bot</th>
                  <th className="px-4 py-3 font-medium">Win Rate</th>
                  <th className="px-4 py-3 font-medium">W-L-D</th>
                  <th className="px-4 py-3 font-medium text-red-400" title="Blunders / Mistakes">Bl/Ms</th>
                  <th className="px-4 py-3 font-medium text-amber-400" title="Avg Centipawn Loss">Avg CP Loss</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {data.bot_performance.sort((a,b) => b.win_rate - a.win_rate).map((bot, i) => (
                  <tr key={bot.bot_id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-4 py-3 font-medium flex items-center gap-2">
                      <span className="text-slate-500 w-4">{i + 1}.</span>
                      {bot.bot_name}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{bot.win_rate.toFixed(1)}%</span>
                        <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500"
                            style={{ width: `${bot.win_rate}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-emerald-400">{bot.wins}</span>-
                      <span className="text-red-400">{bot.losses}</span>-
                      <span className="text-slate-400">{bot.draws}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-red-400 font-medium">{bot.total_blunders}</span> / <span className="text-amber-500">{bot.total_mistakes}</span>
                    </td>
                    <td className="px-4 py-3 font-mono">
                      {(bot.avg_eval_loss * 100).toFixed(0)}
                    </td>
                  </tr>
                ))}
                {data.bot_performance.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                      No matches played yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Critical Moments */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden flex flex-col h-[500px]">
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <AlertTriangle size={20} className="text-amber-400" />
              Critical AI Insights
            </h2>
          </div>
          <div className="p-4 overflow-y-auto flex-1 space-y-4">
            {data.ai_insights.map((insight, i) => (
              <div key={i} className="bg-slate-700/30 p-3 rounded-lg border border-slate-700">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${insight.color === 'white' ? 'bg-white' : 'bg-black border border-slate-600'}`}></span>
                    <span className="font-semibold text-sm">Move {insight.move_number}: {insight.move}</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded font-medium ${insight.loss >= 1.5 ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}`}>
                    {insight.loss >= 1.5 ? 'Blunder' : 'Mistake'}
                  </span>
                </div>
                <p className="text-sm text-slate-300 italic mb-2">
                  {insight.commentary}
                </p>
                <div className="text-xs text-slate-500 font-mono flex justify-between items-center">
                  <Link to={`/match?id=${insight.match_id}`} className="text-blue-400 hover:underline">
                    Match #{insight.match_id}
                  </Link>
                  <span>Eval: {insight.eval_before > 0 ? '+' : ''}{insight.eval_before.toFixed(1)} ➔ {insight.eval_after > 0 ? '+' : ''}{insight.eval_after.toFixed(1)}</span>
                </div>
              </div>
            ))}
            {data.ai_insights.length === 0 && (
              <div className="text-center py-8 text-slate-500 mt-10">
                <XCircle size={32} className="mx-auto mb-2 opacity-50" />
                <p>No critical insights yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
