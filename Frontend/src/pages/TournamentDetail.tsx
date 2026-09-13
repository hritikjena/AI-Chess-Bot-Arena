import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Trophy, ArrowLeft, Play, Cpu, Zap, Activity } from 'lucide-react';
import { BentoGrid } from '../components/bento/BentoGrid';
import { BentoCard } from '../components/bento/BentoCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'REGISTRATION_OPEN': return <Badge variant="success">Registration Open</Badge>;
      case 'RUNNING': return <Badge variant="accent" className="animate-pulse">Running</Badge>;
      case 'COMPLETED': return <Badge variant="default">Completed</Badge>;
      default: return <Badge variant="warning">{status.replace('_', ' ')}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-arena-muted flex flex-col items-center gap-4">
          <Trophy className="animate-bounce" size={32} />
          <p className="font-mono text-sm tracking-widest uppercase">Loading Championship...</p>
        </div>
      </div>
    );
  }
  
  if (!tournament) return <div className="text-center text-danger py-12">Tournament not found.</div>;

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto pb-12">
      
      {/* Header */}
      <div>
        <Link to="/tournaments" className="inline-flex items-center gap-2 text-arena-muted hover:text-arena-primary transition-colors mb-6 font-mono text-sm uppercase tracking-widest">
          <ArrowLeft size={16} /> Back to Tournaments
        </Link>
        <div className="flex flex-col md:flex-row items-start md:items-end justify-between gap-6 pb-6 border-b border-arena">
          <div>
            <h1 className="text-4xl font-display font-medium text-arena-primary tracking-wide">
              {tournament.name}
            </h1>
            <p className="text-sm text-arena-secondary mt-2 font-light">
              {tournament.description || 'Knockout Championship'}
            </p>
          </div>
          <div>
            {getStatusBadge(tournament.status)}
          </div>
        </div>
      </div>

      <BentoGrid columns={4}>
        
        {/* Registration Sidebar */}
        <div className="col-span-1 flex flex-col gap-6">
          <BentoCard title="Registration">
            <div className="flex justify-between items-center mb-6 text-sm">
              <span className="text-arena-muted font-mono uppercase tracking-widest">Enrolled</span>
              <span className="font-display font-semibold text-arena-primary text-xl">
                {participants.length} <span className="text-arena-muted font-light text-base">/ {tournament.participant_limit}</span>
              </span>
            </div>

            {tournament.status === 'REGISTRATION_OPEN' ? (
              <form onSubmit={handleRegister} className="space-y-4">
                <div className="relative">
                  <select 
                    className="w-full bg-transparent border border-arena text-arena-primary rounded-lg px-4 py-3 focus:outline-none focus:ring-1 focus:ring-arena-accent appearance-none font-medium"
                    value={selectedBot}
                    onChange={(e) => setSelectedBot(e.target.value)}
                    required
                  >
                    <option value="" className="bg-arena-bg">-- Select Engine --</option>
                    {bots.map(b => (
                      <option key={b.id} value={b.id} className="bg-arena-bg">{b.name}</option>
                    ))}
                  </select>
                </div>
                <Button 
                  type="submit"
                  disabled={registering || !selectedBot}
                  className="w-full justify-center"
                >
                  {registering ? 'Registering...' : 'Deploy Engine'}
                </Button>
              </form>
            ) : (
              <div className="text-center p-4 neu-inset rounded-lg text-arena-secondary font-mono text-sm uppercase tracking-widest">
                Registration Closed
              </div>
            )}
            
            {tournament.status === 'REGISTRATION_OPEN' && (
              <div className="mt-6 pt-6 border-t border-arena">
                <Button 
                  variant="primary"
                  onClick={async () => {
                    if (confirm('Initiate championship sequence? Registration will be permanently closed.')) {
                      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/${id}/start`, { method: 'POST' });
                      if (res.ok) fetchTournament();
                      else alert('Failed to initiate. Ensure sufficient engines are deployed.');
                    }
                  }}
                  className="w-full justify-center flex items-center gap-2"
                >
                  <Zap size={16} />
                  Initiate Bracket
                </Button>
              </div>
            )}
          </BentoCard>

          <BentoCard title="Competitors" className="flex-1">
            <ul className="space-y-2">
              {participants.length === 0 ? (
                <li className="text-arena-muted font-light text-sm italic">No engines deployed yet.</li>
              ) : (
                participants.map((p) => {
                  return (
                    <li key={p.id} className="flex justify-between items-center bg-white/[0.02] p-3 rounded-lg border border-arena/50 hover:border-arena transition-colors group">
                      <div className="flex items-center gap-3">
                        <Cpu size={14} className="text-arena-muted group-hover:text-arena-accent transition-colors" />
                        <span className="font-medium text-arena-primary text-sm">{getBotName(p.bot_id)}</span>
                      </div>
                      {p.seed && (
                        <span className="text-[10px] font-mono font-bold bg-white/5 text-arena-secondary px-2 py-1 rounded">
                          S{p.seed}
                        </span>
                      )}
                    </li>
                  )
                })
              )}
            </ul>
          </BentoCard>
        </div>

        {/* Main Area: Bracket & Games */}
        <BentoCard 
          colSpan={3} 
          title="Championship Bracket"
          className="min-h-[500px]"
        >
          {matches.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[300px] text-center gap-6">
              <div className="relative">
                <Trophy className="text-arena-muted opacity-50" size={64} strokeWidth={1} />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-24 h-24 border border-arena-muted/30 rounded-full animate-[spin_10s_linear_infinite] border-t-transparent" />
                </div>
              </div>
              <div>
                <h2 className="text-2xl font-display font-medium text-arena-primary mb-2">Awaiting Bracket Generation</h2>
                <p className="text-arena-secondary font-light">The knockout framework will construct once registration concludes.</p>
              </div>
            </div>
          ) : (
            <div className="flex gap-8 overflow-x-auto pb-8 pt-4 custom-scrollbar">
              {sortedRounds.map((roundName) => (
                <div key={roundName} className="flex-none w-72 flex flex-col justify-around gap-6 relative">
                  <h4 className="text-center font-mono text-xs uppercase tracking-widest text-arena-muted mb-4 pb-2 border-b border-arena/50">
                    {roundName}
                  </h4>
                  {rounds[roundName].map((match: any) => (
                    <div 
                      key={match.id} 
                      className={`
                        bg-white/[0.02] rounded-xl border relative transition-all duration-300
                        ${match.status === 'RUNNING' 
                          ? 'border-arena-accent shadow-[0_0_15px_rgba(201,162,109,0.15)]' 
                          : 'border-arena/80 hover:border-arena'
                        }
                      `}
                    >
                      {/* Player 1 (White) */}
                      <div className="p-4 border-b border-arena/50 flex justify-between items-center">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-[#e2e8f0]" />
                          <span className={`font-medium text-sm ${match.winner_id === match.bot1_id ? 'text-arena-accent' : 'text-arena-primary'}`}>
                            {getBotName(match.bot1_id)}
                          </span>
                        </div>
                        {match.winner_id === match.bot1_id && <Badge variant="success">WIN</Badge>}
                      </div>
                      
                      {/* Player 2 (Black) */}
                      <div className="p-4 flex justify-between items-center bg-white/[0.01] rounded-b-xl">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-[#2d333b] border border-arena" />
                          <span className={`font-medium text-sm ${match.winner_id === match.bot2_id ? 'text-arena-accent' : 'text-arena-primary'}`}>
                            {getBotName(match.bot2_id)}
                          </span>
                        </div>
                        {match.winner_id === match.bot2_id && <Badge variant="success">WIN</Badge>}
                      </div>
                      
                      {/* Match Status / Link */}
                      <div className="absolute -right-3 -top-3 z-10">
                        {match.status === 'COMPLETED' ? (
                          <Link 
                            to={`/match?matchId=${match.id}`} 
                            className="w-8 h-8 flex items-center justify-center bg-arena-accent hover:bg-arena-accent/90 text-white rounded-full shadow-lg transition-transform hover:scale-110" 
                            title="Analyze Match"
                          >
                            <Play size={14} fill="currentColor" className="ml-0.5" />
                          </Link>
                        ) : match.status === 'RUNNING' ? (
                          <div 
                            className="w-8 h-8 flex items-center justify-center bg-success text-white rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)] animate-pulse" 
                            title="Match in progress"
                          >
                            <Activity size={14} />
                          </div>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </BentoCard>

      </BentoGrid>
    </div>
  );
}
