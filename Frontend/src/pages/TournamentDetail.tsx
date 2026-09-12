import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Trophy, Calendar as CalendarIcon, Users, ArrowLeft, Play, ExternalLink } from 'lucide-react';

export default function TournamentDetail() {
  const { id } = useParams();
  const [tournament, setTournament] = useState<any>(null);
  const [participants, setParticipants] = useState<any[]>([]);
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [bots, setBots] = useState<any[]>([]);
  const [selectedBot, setSelectedBot] = useState('');

  const fetchTournament = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/${id}`);
      if (res.ok) setTournament(await res.json());
      
      const partRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/${id}/participants`);
      if (partRes.ok) setParticipants(await partRes.json());

      const matchesRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/${id}/matches`);
      if (matchesRes.ok) setMatches(await matchesRes.json());

      const botsRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/bots/`);
      if (botsRes.ok) setBots(await botsRes.json());

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTournament();
    
    // Auto-refresh matches every 5 seconds if tournament is RUNNING
    const intervalId = setInterval(() => {
        if (tournament && tournament.status === 'RUNNING') {
            fetchTournament();
        }
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, [id, tournament?.status]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBot) return;
    setRegistering(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/${id}/register?bot_id=${selectedBot}`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchTournament();
        setSelectedBot('');
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to register');
      }
    } catch (err) {
      console.error(err);
    }
    setRegistering(false);
  };

  const getBotName = (botId: number | null) => {
    if (!botId) return 'TBD';
    const bot = bots.find(b => b.id === botId);
    return bot ? bot.name : `Bot #${botId}`;
  };

  // Group matches by round for bracket
  const rounds = matches.reduce((acc: any, match: any) => {
    if (!acc[match.round_name]) {
      acc[match.round_name] = [];
    }
    acc[match.round_name].push(match);
    return acc;
  }, {});

  // Sort rounds (naive approach, usually we sort by sequence or size)
  const sortedRounds = Object.keys(rounds).sort((a, b) => {
    return rounds[b].length - rounds[a].length;
  });

  if (loading) return <div className="text-center text-slate-400 py-12">Loading...</div>;
  if (!tournament) return <div className="text-center text-red-400 py-12">Tournament not found.</div>;

  return (
    <div className="animate-in fade-in duration-500 max-w-7xl mx-auto space-y-8 pb-12">
      
      <div>
        <Link to="/tournaments" className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6">
          <ArrowLeft size={20} /> Back to Tournaments
        </Link>
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
              <Trophy className="text-amber-500" size={40} />
              {tournament.name}
            </h1>
            <p className="text-slate-400 mt-2 text-lg">{tournament.description || 'Knockout Championship'}</p>
          </div>
          <div className="bg-slate-800 px-6 py-3 rounded-xl border border-slate-700 font-bold text-blue-400 tracking-wider">
            {tournament.status.replace('_', ' ')}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        
        {/* Registration Sidebar */}
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 shadow-xl">
            <h3 className="font-bold text-white mb-4 text-lg border-b border-slate-700 pb-2">Registration</h3>
            <div className="flex justify-between items-center mb-6">
              <span className="text-slate-400 text-sm">Registered</span>
              <span className="font-bold text-white">{participants.length} / {tournament.participant_limit}</span>
            </div>

            {tournament.status === 'REGISTRATION_OPEN' ? (
              <form onSubmit={handleRegister} className="space-y-4">
                <select 
                  className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                  value={selectedBot}
                  onChange={(e) => setSelectedBot(e.target.value)}
                  required
                >
                  <option value="">-- Select Bot --</option>
                  {bots.map(b => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
                <button 
                  type="submit"
                  disabled={registering || !selectedBot}
                  className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-3 rounded-lg transition-all disabled:opacity-50"
                >
                  {registering ? 'Registering...' : 'Register Bot'}
                </button>
              </form>
            ) : (
              <div className="text-center p-4 bg-slate-900/50 rounded-lg text-slate-400 font-semibold border border-slate-700">
                Registration Closed
              </div>
            )}
          </div>

          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 shadow-xl">
            <h3 className="font-bold text-white mb-4 text-lg border-b border-slate-700 pb-2">Participants</h3>
            <ul className="space-y-2">
              {participants.length === 0 ? (
                <li className="text-slate-500 text-sm italic">No participants yet.</li>
              ) : (
                participants.map(p => {
                  return (
                    <li key={p.id} className="flex justify-between items-center bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                      <span className="font-semibold text-slate-200">{getBotName(p.bot_id)}</span>
                      {p.seed && <span className="text-xs font-bold bg-blue-900 text-blue-300 px-2 py-1 rounded">Seed {p.seed}</span>}
                    </li>
                  )
                })
              )}
            </ul>
            
            {tournament.status === 'REGISTRATION_OPEN' && (
              <div className="mt-6 pt-4 border-t border-slate-700">
                <button 
                  onClick={async () => {
                    if (confirm('Are you sure you want to start the tournament? Registration will close.')) {
                      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/${id}/start`, { method: 'POST' });
                      if (res.ok) fetchTournament();
                      else alert('Failed to start. Ensure enough bots are registered.');
                    }
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition-all"
                >
                  Start Tournament
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Main Area: Bracket & Games */}
        <div className="xl:col-span-3">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 shadow-xl min-h-[400px]">
            <h3 className="font-bold text-white mb-6 text-xl flex items-center gap-2">
              <Trophy className="text-amber-500" />
              Tournament Bracket
            </h3>
            
            {matches.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-[300px] text-center">
                <Trophy className="text-slate-600 mb-4" size={48} />
                <h2 className="text-2xl font-bold text-slate-400">Bracket Generation Pending</h2>
                <p className="text-slate-500 mt-2">The knockout bracket will appear here once registration closes.</p>
              </div>
            ) : (
              <div className="flex gap-8 overflow-x-auto pb-8">
                {sortedRounds.map((roundName, roundIdx) => (
                  <div key={roundName} className="flex-none w-72 flex flex-col justify-around gap-4 relative">
                    <h4 className="text-center font-bold text-slate-400 mb-4">{roundName}</h4>
                    {rounds[roundName].map((match: any) => (
                      <div key={match.id} className={`bg-slate-900 rounded-lg border flex flex-col ${match.status === 'RUNNING' ? 'border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]' : 'border-slate-700'} relative`}>
                        <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900 rounded-t-lg">
                          <span className={`font-semibold ${match.winner_id === match.bot1_id ? 'text-amber-400' : 'text-slate-200'}`}>
                            {getBotName(match.bot1_id)}
                          </span>
                          {match.winner_id === match.bot1_id && <span className="text-xs font-bold text-green-500">WIN</span>}
                        </div>
                        <div className="p-3 flex justify-between items-center bg-slate-800/50 rounded-b-lg">
                          <span className={`font-semibold ${match.winner_id === match.bot2_id ? 'text-amber-400' : 'text-slate-200'}`}>
                            {getBotName(match.bot2_id)}
                          </span>
                          {match.winner_id === match.bot2_id && <span className="text-xs font-bold text-green-500">WIN</span>}
                        </div>
                        
                        {/* Match Status / Link */}
                        <div className="absolute -right-4 -top-3">
                          {match.status === 'COMPLETED' ? (
                            <Link to={`/match?matchId=${match.id}`} className="bg-blue-600 hover:bg-blue-500 text-white p-1.5 rounded-full shadow-lg block transition-transform hover:scale-110" title="Replay Match">
                              <Play size={14} fill="currentColor" />
                            </Link>
                          ) : match.status === 'RUNNING' ? (
                            <div className="bg-green-600 text-white p-1.5 rounded-full shadow-lg animate-pulse" title="Running live in backend">
                              <Play size={14} fill="currentColor" />
                            </div>
                          ) : null}
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
            
          </div>
        </div>

      </div>

    </div>
  );
}
