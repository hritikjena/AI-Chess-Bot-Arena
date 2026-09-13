import React, { useState, useEffect, useRef } from 'react';
import { Chessboard } from 'react-chessboard';
import { Play, Square, ArrowLeft, ArrowRight, SkipForward, SkipBack, BrainCircuit, Activity } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { Chess } from 'chess.js';
import { BentoGrid } from '../components/bento/BentoGrid';
import { BentoCard } from '../components/bento/BentoCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

interface GameState {
  status: string;
  fen: string;
  white_points: number;
  black_points: number;
  last_move: string | null;
  move_number: number;
  error: string | null;
  result?: string;
  reason?: string;
  commentary?: string | null;
}

export default function Match() {
  const [searchParams] = useSearchParams();
  const replayMatchId = searchParams.get('matchId');
  
  const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
  const [fen, setFen] = useState(START_FEN);
  const [status, setStatus] = useState<string>('idle');
  const [, setMatchId] = useState<number | null>(replayMatchId ? parseInt(replayMatchId) : null);
  const [whitePoints, setWhitePoints] = useState(0);
  const [blackPoints, setBlackPoints] = useState(0);
  const [moveHistory, setMoveHistory] = useState<string[]>([]);
  const [commentary, setCommentary] = useState<string | null>(null);
  
  // Replay State
  const [isReplayMode] = useState(!!replayMatchId);
  const [replayMoves, setReplayMoves] = useState<string[]>([]);
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const chessRef = useRef(new Chess());
  const [isPlaying, setIsPlaying] = useState(false);
  const playIntervalRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const ws = useRef<WebSocket | null>(null);

  const [bots, setBots] = useState<{id: number, name: string}[]>([]);
  const [bot1, setBot1] = useState<number | null>(null);
  const [bot2, setBot2] = useState<number | null>(null);
  
  const [matchInfo, setMatchInfo] = useState<any>(null);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL}/bots/`)
      .then(res => res.json())
      .then(data => {
         setBots(data);
         if(data.length >= 2 && !isReplayMode) {
             setBot1(data[0].id);
             setBot2(data[1].id);
         }
      })
      .catch(err => console.error("Failed to fetch bots:", err));
  }, [isReplayMode]);

  useEffect(() => {
    if (isReplayMode && replayMatchId) {
      // Fetch match data
      fetch(`${import.meta.env.VITE_API_BASE_URL}/matches/${replayMatchId}`)
        .then(res => res.json())
        .then(data => {
          setMatchInfo(data);
          setBot1(data.bot1_id);
          setBot2(data.bot2_id);
          setReplayMoves(data.moves || []);
          setStatus('completed');
          if (data.commentary) setCommentary(data.commentary);
        });
    }
  }, [isReplayMode, replayMatchId]);

  // Handle Playback step
  useEffect(() => {
    if (!isReplayMode) return;
    
    chessRef.current.reset();
    for (let i = 0; i <= currentMoveIndex; i++) {
      if (i < replayMoves.length) {
        try {
          chessRef.current.move(replayMoves[i]);
        } catch (e) {
          console.error("Invalid move in replay:", replayMoves[i]);
        }
      }
    }
    setFen(chessRef.current.fen());
    setMoveHistory(replayMoves.slice(0, currentMoveIndex + 1));
  }, [currentMoveIndex, replayMoves, isReplayMode]);
  
  // Auto play
  useEffect(() => {
    if (isPlaying) {
      playIntervalRef.current = setInterval(() => {
        setCurrentMoveIndex(prev => {
          if (prev >= replayMoves.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    } else {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    }
    return () => {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    };
  }, [isPlaying, replayMoves.length]);

  const startMatch = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/matches/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot1_id: bot1, bot2_id: bot2, max_moves: 200 })
      });
      
      if (!response.ok) {
        console.error("Failed to create match");
        setStatus('error');
        return;
      }
      
      const matchData = await response.json();
      const newMatchId = matchData.id;
      
      setMatchId(newMatchId);
      setStatus('playing');
      setMoveHistory([]);
      setFen(START_FEN);
      setWhitePoints(0);
      setBlackPoints(0);
      setCommentary(null);
      
      if (ws.current) ws.current.close();
      
      ws.current = new WebSocket(`${import.meta.env.VITE_WS_BASE_URL}/ws/match/${newMatchId}`);
      
      ws.current.onmessage = (event) => {
        const state: GameState = JSON.parse(event.data);
        if (state.error) {
          setStatus('error');
          return;
        }
        
        setFen(state.fen);
        setWhitePoints(state.white_points);
        setBlackPoints(state.black_points);
        
        if (state.last_move) {
          setMoveHistory(prev => [...prev, state.last_move!]);
        }
        
        if (state.commentary) {
          setCommentary(state.commentary);
        }
        
        if (state.status === 'completed' || state.status === 'finished') {
          setStatus('completed');
          ws.current?.close();
        }
      };

      ws.current.onclose = () => {
        if (status === 'playing') setStatus('disconnected');
      };
    } catch (e) {
      console.error("Failed to connect websocket", e);
      setStatus('error');
    }
  };

  const stopMatch = () => {
    if (ws.current) ws.current.close();
    setStatus('idle');
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto">
      
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-arena">
        <div>
          <h1 className="text-4xl font-display font-medium text-arena-primary tracking-wide">
            {isReplayMode ? 'Match Replay' : 'Live Match Arena'}
          </h1>
          <p className="text-sm text-arena-secondary mt-2 font-light flex items-center gap-2">
            {isReplayMode && matchInfo ? (
              <>
                <span className="font-mono uppercase tracking-widest text-arena-muted">{matchInfo.round_name}</span>
                <span className="w-1 h-1 rounded-full bg-arena-muted" />
                <span>{matchInfo.result}</span>
                <span className="w-1 h-1 rounded-full bg-arena-muted" />
                <span className="italic">{matchInfo.reason}</span>
              </>
            ) : (
              'Observe autonomous chess engines compete in real-time.'
            )}
          </p>
        </div>
        
        {/* Match Setup Controls */}
        <div className="flex items-center gap-4 bg-white/[0.02] p-2 rounded-xl border border-arena">
          <select 
            value={bot1 || ''} 
            onChange={(e) => setBot1(Number(e.target.value))}
            disabled={status === 'playing' || isReplayMode}
            className="bg-transparent text-arena-primary border-none rounded-lg px-4 py-2 focus:ring-1 focus:ring-arena-accent outline-none font-medium appearance-none cursor-pointer disabled:opacity-50"
          >
            {bots.map(b => <option key={`w-${b.id}`} value={b.id} className="bg-arena-bg">{b.name} (White)</option>)}
          </select>
          
          <span className="text-arena-muted font-display italic px-2">vs</span>
          
          <select 
            value={bot2 || ''} 
            onChange={(e) => setBot2(Number(e.target.value))}
            disabled={status === 'playing' || isReplayMode}
            className="bg-transparent text-arena-primary border-none rounded-lg px-4 py-2 focus:ring-1 focus:ring-arena-accent outline-none font-medium appearance-none cursor-pointer disabled:opacity-50"
          >
            {bots.map(b => <option key={`b-${b.id}`} value={b.id} className="bg-arena-bg">{b.name} (Black)</option>)}
          </select>
          
          {!isReplayMode && (
            status !== 'playing' ? (
              <Button onClick={startMatch} className="flex items-center gap-2 ml-2">
                <Play size={16} /> Deploy
              </Button>
            ) : (
              <Button onClick={stopMatch} variant="danger" className="flex items-center gap-2 ml-2">
                <Square size={16} /> Halt
              </Button>
            )
          )}
        </div>
      </div>

      <BentoGrid columns={3}>
        
        {/* Main Chessboard Area */}
        <BentoCard colSpan={2} noPadding className="flex flex-col h-full min-h-[600px]">
          
          {/* Opponent (Black) Info */}
          <div className="p-6 border-b border-arena/50 flex justify-between items-center bg-white/[0.01]">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 neu-inset rounded-xl flex items-center justify-center text-2xl">
                ♟️
              </div>
              <div>
                <h3 className="font-display font-medium text-xl text-arena-primary">
                  {bots.find(b => b.id === bot2)?.name || 'Loading...'}
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs font-mono uppercase tracking-widest text-arena-muted">Black</span>
                  {matchInfo?.winner_id === bot2 && (
                    <Badge variant="success">Winner</Badge>
                  )}
                </div>
              </div>
            </div>
            {!isReplayMode && (
              <div className="text-right">
                <span className="text-3xl font-display font-semibold text-arena-primary">{blackPoints}</span>
                <span className="text-arena-muted text-xs font-mono uppercase tracking-widest ml-2">pts</span>
              </div>
            )}
          </div>

          {/* Board Container */}
          <div className="flex-1 flex flex-col items-center justify-center p-8 relative">
            
            {/* Status Indicator overlay if not idle */}
            {status !== 'idle' && (
              <div className="absolute top-4 right-4 flex items-center gap-2">
                <span className="relative flex h-3 w-3">
                  {status === 'playing' && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>}
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${
                    status === 'playing' ? 'bg-success' : 
                    status === 'completed' ? 'bg-warning' : 
                    status === 'error' ? 'bg-danger' : 'bg-arena-muted'
                  }`}></span>
                </span>
                <span className="text-xs font-mono uppercase tracking-widest text-arena-muted">
                  {status}
                </span>
              </div>
            )}

            <div className="w-full max-w-[500px] aspect-square rounded-sm overflow-hidden neu-raised">
              <Chessboard 
                options={{
                  position: fen,
                  darkSquareStyle: { backgroundColor: '#2d333b' },
                  lightSquareStyle: { backgroundColor: '#e2e8f0' },
                  animationDurationInMs: 200,
                  boardStyle: {
                    borderRadius: '2px',
                    boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)'
                  }
                }}
              />
            </div>
            
            {/* Playback Controls (Replay Only) */}
            {isReplayMode && (
              <div className="mt-8 flex items-center justify-center gap-4 neu-inset p-3 rounded-full">
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(-1); }}
                  className="p-2 text-arena-muted hover:text-arena-primary transition-colors"
                >
                  <SkipBack size={20} />
                </button>
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(p => Math.max(-1, p - 1)); }}
                  className="p-2 text-arena-muted hover:text-arena-primary transition-colors"
                >
                  <ArrowLeft size={20} />
                </button>
                
                <button 
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-12 h-12 flex items-center justify-center bg-arena-accent text-white rounded-full transition-transform hover:scale-105 shadow-[0_4px_20px_rgba(201,162,109,0.3)]"
                >
                  {isPlaying ? <Square size={20} /> : <Play size={20} className="ml-1" />}
                </button>
                
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(p => Math.min(replayMoves.length - 1, p + 1)); }}
                  className="p-2 text-arena-muted hover:text-arena-primary transition-colors"
                >
                  <ArrowRight size={20} />
                </button>
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(replayMoves.length - 1); }}
                  className="p-2 text-arena-muted hover:text-arena-primary transition-colors"
                >
                  <SkipForward size={20} />
                </button>
                <div className="ml-4 font-mono text-sm text-arena-muted w-16 text-center border-l border-arena pl-4">
                  {currentMoveIndex + 1}/{replayMoves.length}
                </div>
              </div>
            )}
            
            {/* Debug FEN */}
            <div className="mt-4 text-center text-[10px] text-arena-muted font-mono opacity-50 max-w-md truncate">
              {fen}
            </div>
          </div>

          {/* Player (White) Info */}
          <div className="p-6 border-t border-arena/50 flex justify-between items-center bg-white/[0.01]">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-[#e2e8f0] text-[#2d333b] rounded-xl flex items-center justify-center text-2xl shadow-inner">
                ♙
              </div>
              <div>
                <h3 className="font-display font-medium text-xl text-arena-primary">
                  {bots.find(b => b.id === bot1)?.name || 'Loading...'}
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs font-mono uppercase tracking-widest text-arena-muted">White</span>
                  {matchInfo?.winner_id === bot1 && (
                    <Badge variant="success">Winner</Badge>
                  )}
                </div>
              </div>
            </div>
            {!isReplayMode && (
              <div className="text-right">
                <span className="text-3xl font-display font-semibold text-arena-primary">{whitePoints}</span>
                <span className="text-arena-muted text-xs font-mono uppercase tracking-widest ml-2">pts</span>
              </div>
            )}
          </div>
        </BentoCard>

        {/* Sidebar panels */}
        <div className="col-span-1 space-y-6 flex flex-col">
          
          {/* AI Commentary Panel */}
          {commentary && (
            <BentoCard className="border-arena-accent/30 shadow-[0_0_30px_rgba(201,162,109,0.1)] relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                <BrainCircuit size={100} />
              </div>
              <h3 className="text-sm font-mono uppercase tracking-widest text-arena-accent flex items-center gap-2 mb-4 relative z-10">
                <BrainCircuit size={16} />
                Grandmaster Analysis
              </h3>
              <p className="text-arena-primary italic font-light leading-relaxed relative z-10">
                "{commentary}"
              </p>
            </BentoCard>
          )}
          
          {/* Move History */}
          <BentoCard title="Move Log" className="flex-1 flex flex-col min-h-[400px]">
            <div className="flex-1 overflow-y-auto pr-2 -mr-2 space-y-1">
              {moveHistory.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-arena-muted gap-4 opacity-50">
                  <Activity size={32} strokeWidth={1} />
                  <span className="font-mono text-xs uppercase tracking-widest">Awaiting Initial Move</span>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                  {moveHistory.reduce((result: string[][], _, index, array) => {
                    if (index % 2 === 0) result.push(array.slice(index, index + 2));
                    return result;
                  }, []).map((pair, idx) => (
                    <React.Fragment key={idx}>
                      <div className="text-arena-primary font-mono flex items-center gap-3">
                        <span className="text-arena-muted text-xs w-6">{idx + 1}.</span> 
                        <span className={`px-2 py-0.5 rounded transition-colors ${isReplayMode && currentMoveIndex === idx * 2 ? 'bg-arena-accent/20 text-arena-accent' : ''}`}>
                          {pair[0]}
                        </span>
                      </div>
                      <div className="text-arena-primary font-mono flex items-center">
                        {pair[1] && (
                          <span className={`px-2 py-0.5 rounded transition-colors ${isReplayMode && currentMoveIndex === idx * 2 + 1 ? 'bg-arena-accent/20 text-arena-accent' : ''}`}>
                            {pair[1]}
                          </span>
                        )}
                      </div>
                    </React.Fragment>
                  ))}
                </div>
              )}
            </div>
          </BentoCard>
          
        </div>
      </BentoGrid>
    </div>
  );
}
