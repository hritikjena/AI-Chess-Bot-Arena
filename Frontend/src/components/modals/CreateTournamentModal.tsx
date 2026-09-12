import React, { useState } from 'react';
import { X, Calendar, Users, Trophy } from 'lucide-react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
        
        <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-900/50">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Trophy className="text-amber-500" size={24} />
            Create Tournament
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          <div className="space-y-1">
            <label className="text-sm font-semibold text-slate-300 block">Tournament Name</label>
            <input 
              type="text" 
              required
              placeholder="e.g., September Championship"
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold text-slate-300 block">Description</label>
            <textarea 
              placeholder="Optional details..."
              rows={2}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-300 flex items-center gap-1">
                <Trophy size={16} /> Format
              </label>
              <select 
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                value={formData.format}
                onChange={(e) => setFormData({...formData, format: e.target.value})}
              >
                <option value="KNOCKOUT">Knockout</option>
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-300 flex items-center gap-1">
                <Users size={16} /> Participant Limit
              </label>
              <select 
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                value={formData.participant_limit}
                onChange={(e) => setFormData({...formData, participant_limit: parseInt(e.target.value)})}
              >
                <option value={4}>4 Bots</option>
                <option value={8}>8 Bots</option>
                <option value={16}>16 Bots</option>
                <option value={32}>32 Bots</option>
              </select>
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t border-slate-800">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Calendar size={16} /> Schedule (Optional)
            </h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-400 block">Registration Start</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  value={formData.registration_start}
                  onChange={(e) => setFormData({...formData, registration_start: e.target.value})}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-400 block">Registration End</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  value={formData.registration_end}
                  onChange={(e) => setFormData({...formData, registration_end: e.target.value})}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-400 block">Tournament Start</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  value={formData.tournament_start}
                  onChange={(e) => setFormData({...formData, tournament_start: e.target.value})}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-400 block">Tournament End</label>
                <input 
                  type="datetime-local" 
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  value={formData.tournament_end}
                  onChange={(e) => setFormData({...formData, tournament_end: e.target.value})}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-6">
            <button 
              type="button" 
              onClick={onClose}
              className="px-5 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 font-semibold transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-lg font-bold shadow-lg shadow-blue-900/30 transition-all active:scale-95 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Tournament'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
