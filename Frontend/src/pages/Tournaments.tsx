import { useState, useEffect } from 'react';
import { Trophy, Calendar as CalendarIcon, Users, Plus, ShieldAlert } from 'lucide-react';
import { Link } from 'react-router-dom';
import CreateTournamentModal from '../components/modals/CreateTournamentModal';
import { BentoGrid } from '../components/bento/BentoGrid';
import { BentoCard } from '../components/bento/BentoCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

interface Tournament {
  id: number;
  name: string;
  description: string;
  format: string;
  status: string;
  participant_limit: number;
  registration_start: string | null;
  registration_end: string | null;
  tournament_start: string | null;
  tournament_end: string | null;
}

export default function Tournaments() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchTournaments = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/`);
      const data = await response.json();
      setTournaments(data);
    } catch (err) {
      console.error('Failed to fetch tournaments', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTournaments();
  }, []);

  const activeTournaments = tournaments.filter(t => ['DRAFT', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'RUNNING'].includes(t.status));
  const pastTournaments = tournaments.filter(t => ['COMPLETED', 'CANCELLED'].includes(t.status));

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'TBD';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'REGISTRATION_OPEN': return <Badge variant="success">Registration Open</Badge>;
      case 'RUNNING': return <Badge variant="accent" className="animate-pulse">Running</Badge>;
      case 'COMPLETED': return <Badge variant="default">Completed</Badge>;
      default: return <Badge variant="warning">{status.replace('_', ' ')}</Badge>;
    }
  };

  const renderTournamentCard = (t: Tournament) => (
    <BentoCard key={t.id} noPadding className="group hover:-translate-y-1 transition-transform duration-300 flex flex-col h-full">
      <div className="p-6 border-b border-arena/50 bg-white/[0.02]">
        <div className="flex justify-between items-start mb-2">
          <span className="text-[10px] font-mono uppercase tracking-widest text-arena-muted">
            Event 0{t.id}
          </span>
          {getStatusBadge(t.status)}
        </div>
        <h3 className="text-2xl font-display font-semibold text-arena-primary mb-2 line-clamp-1">
          {t.name}
        </h3>
        <p className="text-sm text-arena-secondary font-light line-clamp-2 min-h-[2.5rem]">
          {t.description || 'No description provided.'}
        </p>
      </div>
      
      <div className="p-6 flex-1 flex flex-col justify-between space-y-6">
        <div className="space-y-3">
          <div className="flex items-center gap-3 text-sm font-mono text-arena-muted">
            <CalendarIcon size={14} className="text-arena-accent" />
            <span>{formatDate(t.tournament_start)} &rarr; {formatDate(t.tournament_end)}</span>
          </div>
          <div className="flex items-center gap-3 text-sm font-mono text-arena-muted">
            <Trophy size={14} className="text-success" />
            <span>{t.format}</span>
          </div>
          <div className="flex items-center gap-3 text-sm font-mono text-arena-muted">
            <Users size={14} className="text-arena-primary" />
            <span>Max {t.participant_limit} Engines</span>
          </div>
        </div>
        
        <Link to={`/tournaments/${t.id}`} className="block">
          <Button variant="secondary" className="w-full justify-center">
            View Championship
          </Button>
        </Link>
      </div>
    </BentoCard>
  );

  return (
    <div className="space-y-12 animate-in fade-in duration-500 max-w-7xl mx-auto pb-12">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-end justify-between gap-6 pb-6 border-b border-arena">
        <div>
          <h1 className="text-4xl font-display font-medium text-arena-primary tracking-wide">
            Arena Tournaments
          </h1>
          <p className="text-sm text-arena-secondary mt-2 font-light">
            Organize and observe knockout championships for autonomous engines.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
          <Plus size={18} /> Configure Tournament
        </Button>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="text-arena-muted flex flex-col items-center gap-4">
            <Trophy className="animate-bounce" size={32} />
            <p className="font-mono text-sm tracking-widest uppercase">Loading Events...</p>
          </div>
        </div>
      ) : (
        <div className="space-y-16">
          
          {/* Active Section */}
          <section>
            <div className="flex items-center gap-3 mb-8">
              <h2 className="text-2xl font-display font-medium text-arena-primary">Active Championships</h2>
              <span className="h-px bg-arena/50 flex-1 ml-4" />
            </div>
            
            {activeTournaments.length === 0 ? (
              <div className="neu-inset rounded-2xl p-12 text-center flex flex-col items-center gap-4">
                <ShieldAlert size={32} strokeWidth={1} className="text-arena-muted" />
                <p className="text-arena-secondary font-light">No active tournaments found in the database.</p>
              </div>
            ) : (
              <BentoGrid columns={3}>
                {activeTournaments.map(renderTournamentCard)}
              </BentoGrid>
            )}
          </section>

          {/* Past Section */}
          <section>
            <div className="flex items-center gap-3 mb-8">
              <h2 className="text-2xl font-display font-medium text-arena-muted">Archived Events</h2>
              <span className="h-px bg-arena/50 flex-1 ml-4" />
            </div>
            
            {pastTournaments.length === 0 ? (
              <p className="text-arena-muted font-light text-sm">No past tournaments.</p>
            ) : (
              <BentoGrid columns={3}>
                {pastTournaments.map(renderTournamentCard)}
              </BentoGrid>
            )}
          </section>
          
        </div>
      )}

      <CreateTournamentModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onCreated={fetchTournaments}
      />
    </div>
  );
}
