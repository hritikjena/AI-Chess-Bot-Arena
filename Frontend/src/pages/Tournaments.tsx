import React, { useState, useEffect } from 'react';
import { Trophy, Calendar as CalendarIcon, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import CreateTournamentModal from '../components/modals/CreateTournamentModal';

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

  const renderTournamentCard = (t: Tournament) => (
    <div key={t.id} className="bg-slate-800 rounded-2xl border border-slate-700 p-6 flex flex-col md:flex-row gap-6 shadow-xl hover:border-slate-600 transition-colors">
      <div className="flex-1">
        <h3 className="text-xl font-bold text-white mb-2">{t.name}</h3>
        {t.description && <p className="text-slate-400 text-sm mb-4">{t.description}</p>}
        
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-slate-300 text-sm">
            <CalendarIcon size={16} className="text-blue-400" />
            <span>{formatDate(t.tournament_start)} &rarr; {formatDate(t.tournament_end)}</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300 text-sm">
            <Trophy size={16} className="text-amber-400" />
            <span>{t.format}</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300 text-sm">
            <Users size={16} className="text-green-400" />
            <span>{t.participant_limit} Bots Max</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col justify-between items-end gap-4 min-w-[200px]">
        <div className={`px-3 py-1 rounded-full text-xs font-bold ${
          t.status === 'REGISTRATION_OPEN' ? 'bg-green-900/50 text-green-400 border border-green-800' :
          t.status === 'RUNNING' ? 'bg-blue-900/50 text-blue-400 border border-blue-800 animate-pulse' :
          t.status === 'COMPLETED' ? 'bg-slate-700 text-slate-300 border border-slate-600' :
          'bg-amber-900/50 text-amber-400 border border-amber-800'
        }`}>
          {t.status.replace('_', ' ')}
        </div>
        
        <Link 
          to={`/tournaments/${t.id}`}
          className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-2.5 rounded-lg font-bold transition-all text-center w-full shadow-lg shadow-slate-900/50"
        >
          View Tournament
        </Link>
      </div>
    </div>
  );

  return (
    <div className="animate-in fade-in duration-500 max-w-6xl mx-auto space-y-12 pb-12">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
            <Trophy className="text-amber-500" size={40} />
            Tournaments
          </h1>
          <p className="text-slate-400 mt-2 text-lg">Compete in limited-game knockout championships.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-900/50 hover:scale-105 flex items-center gap-2"
        >
          <span>+</span> New Tournament
        </button>
      </div>

      {loading ? (
        <div className="text-center text-slate-400 py-12">Loading tournaments...</div>
      ) : (
        <div className="space-y-12">
          {/* Active Section */}
          <section className="space-y-6">
            <h2 className="text-xl font-bold text-slate-200 border-b border-slate-700 pb-2">ACTIVE TOURNAMENTS</h2>
            {activeTournaments.length === 0 ? (
              <p className="text-slate-500 italic">No active tournaments found.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {activeTournaments.map(renderTournamentCard)}
              </div>
            )}
          </section>

          {/* Past Section */}
          <section className="space-y-6">
            <h2 className="text-xl font-bold text-slate-200 border-b border-slate-700 pb-2">PAST TOURNAMENTS</h2>
            {pastTournaments.length === 0 ? (
              <p className="text-slate-500 italic">No past tournaments found.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {pastTournaments.map(renderTournamentCard)}
              </div>
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
