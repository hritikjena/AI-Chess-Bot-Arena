import React, { useState } from 'react';
import { X, Calendar, Users, Trophy } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

interface CreateTournamentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export default function CreateTournamentModal({ isOpen, onClose, onCreated }: CreateTournamentModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    format: 'KNOCKOUT',
    participant_limit: 16,
    registration_start: '',
    registration_end: '',
    tournament_start: '',
    tournament_end: ''
  });

  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/tournaments/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          registration_start: formData.registration_start ? new Date(formData.registration_start).toISOString() : null,
          registration_end: formData.registration_end ? new Date(formData.registration_end).toISOString() : null,
          tournament_start: formData.tournament_start ? new Date(formData.tournament_start).toISOString() : null,
          tournament_end: formData.tournament_end ? new Date(formData.tournament_end).toISOString() : null,
        })
      });

      if (response.ok) {
        onCreated();
        onClose();
      } else {
        console.error('Failed to create tournament');
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md animate-in fade-in duration-200 p-4">
      <div className="bg-arena-bg border border-arena rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
        
        <div className="flex items-center justify-between p-6 border-b border-arena bg-white/[0.02]">
          <h2 className="text-xl font-display font-medium text-arena-primary flex items-center gap-2">
            <Trophy className="text-arena-accent" size={24} />
            Configure Event
          </h2>
          <button onClick={onClose} className="text-arena-muted hover:text-arena-primary transition-colors">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          <div className="space-y-1">
            <label className="text-sm font-semibold text-arena-primary block font-display tracking-wide">Tournament Name</label>
            <Input 
              type="text" 
              required
              placeholder="e.g., September Championship"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold text-arena-primary block font-display tracking-wide">Description</label>
            <textarea 
              placeholder="Optional details..."
              rows={2}
              className="w-full bg-white/[0.03] border border-arena/50 text-arena-primary rounded-lg px-4 py-3 focus:outline-none focus:border-arena-accent focus:ring-1 focus:ring-arena-accent transition-all custom-scrollbar placeholder:text-arena-muted"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-semibold text-arena-primary flex items-center gap-2 font-display tracking-wide">
                <Trophy size={14} className="text-arena-muted" /> Format
              </label>
              <select 
                className="w-full bg-white/[0.03] border border-arena/50 text-arena-primary rounded-lg px-4 py-3 focus:outline-none focus:border-arena-accent appearance-none font-medium"
                value={formData.format}
                onChange={(e) => setFormData({...formData, format: e.target.value})}
              >
                <option value="KNOCKOUT" className="bg-arena-bg">Knockout</option>
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-semibold text-arena-primary flex items-center gap-2 font-display tracking-wide">
                <Users size={14} className="text-arena-muted" /> Entrant Limit
              </label>
              <select 
                className="w-full bg-white/[0.03] border border-arena/50 text-arena-primary rounded-lg px-4 py-3 focus:outline-none focus:border-arena-accent appearance-none font-medium"
                value={formData.participant_limit}
                onChange={(e) => setFormData({...formData, participant_limit: parseInt(e.target.value)})}
              >
                <option value={4} className="bg-arena-bg">4 Engines</option>
                <option value={8} className="bg-arena-bg">8 Engines</option>
                <option value={16} className="bg-arena-bg">16 Engines</option>
                <option value={32} className="bg-arena-bg">32 Engines</option>
              </select>
            </div>
          </div>

          <div className="space-y-4 pt-6 border-t border-arena">
            <h3 className="text-xs font-mono font-bold text-arena-muted uppercase tracking-widest flex items-center gap-2">
              <Calendar size={14} /> Schedule Configuration
            </h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-mono uppercase tracking-widest text-arena-muted block">Registration Start</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-white/[0.03] border border-arena/50 text-arena-secondary rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-arena-accent"
                  value={formData.registration_start}
                  onChange={(e) => setFormData({...formData, registration_start: e.target.value})}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[11px] font-mono uppercase tracking-widest text-arena-muted block">Registration End</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-white/[0.03] border border-arena/50 text-arena-secondary rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-arena-accent"
                  value={formData.registration_end}
                  onChange={(e) => setFormData({...formData, registration_end: e.target.value})}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-mono uppercase tracking-widest text-arena-muted block">Tournament Start</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-white/[0.03] border border-arena/50 text-arena-secondary rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-arena-accent"
                  value={formData.tournament_start}
                  onChange={(e) => setFormData({...formData, tournament_start: e.target.value})}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[11px] font-mono uppercase tracking-widest text-arena-muted block">Tournament End</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-white/[0.03] border border-arena/50 text-arena-secondary rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-arena-accent"
                  value={formData.tournament_end}
                  onChange={(e) => setFormData({...formData, tournament_end: e.target.value})}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-6 border-t border-arena">
            <Button 
              variant="secondary"
              type="button" 
              onClick={onClose}
            >
              Cancel
            </Button>
            <Button 
              variant="primary"
              type="submit" 
              disabled={loading}
            >
              {loading ? 'Initializing...' : 'Initialize Event'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
