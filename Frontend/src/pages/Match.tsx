import React, { useState, useEffect, useRef } from 'react';
import { Chessboard } from 'react-chessboard';
import { Play, Square, Trophy, History, ArrowLeft, ArrowRight, SkipForward, SkipBack } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { Chess } from 'chess.js';

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
  const [matchId, setMatchId] = useState<number | null>(replayMatchId ? parseInt(replayMatchId) : null);
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
  const playIntervalRef = useRef<NodeJS.Timeout | null>(null);

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
    <div className="animate-in fade-in duration-500 max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">
            {isReplayMode ? `Match Replay` : `Live Match Arena`}
          </h1>
          {isReplayMode && matchInfo && (
            <p className="text-slate-400 mt-1">{matchInfo.round_name} • {matchInfo.result} • {matchInfo.reason}</p>
          )}
        </div>
        
        {/* Controls */}
        <div className="flex items-center gap-4 bg-slate-800 p-2 rounded-xl border border-slate-700">
          <select 
            value={bot1 || ''} 
            onChange={(e) => setBot1(Number(e.target.value))}
            disabled={status === 'playing' || isReplayMode}
            className="bg-slate-900 text-slate-200 border-none rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none max-w-[200px]"
          >
            {bots.map(b => <option key={`w-${b.id}`} value={b.id}>{b.name} (White)</option>)}
          </select>
          <span className="text-slate-500 font-bold px-2">VS</span>
          <select 
            value={bot2 || ''} 
            onChange={(e) => setBot2(Number(e.target.value))}
            disabled={status === 'playing' || isReplayMode}
            className="bg-slate-900 text-slate-200 border-none rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none max-w-[200px]"
          >
            {bots.map(b => <option key={`b-${b.id}`} value={b.id}>{b.name} (Black)</option>)}
          </select>
          
          {!isReplayMode && (
            status !== 'playing' ? (
              <button 
                onClick={startMatch}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors ml-2"
              >
                <Play size={18} /> Start
              </button>
            ) : (
              <button 
                onClick={stopMatch}
                className="flex items-center gap-2 bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors ml-2"
              >
                <Square size={18} /> Stop
              </button>
            )
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pt-4">
        
        {/* Main Chessboard Area */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 shadow-2xl shadow-black/50">
            
            {/* Opponent (Black) Info */}
            <div className="flex justify-between items-center mb-4 px-2">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center border border-slate-700">
                  <span className="text-xl">♟️</span>
                </div>
                <div>
                  <h3 className="font-bold text-slate-200">{bots.find(b => b.id === bot2)?.name || 'Loading...'}</h3>
                  <p className="text-sm text-slate-400">Playing Black {matchInfo?.winner_id === bot2 && <span className="text-green-500 font-bold ml-2">(Winner)</span>}</p>
                </div>
              </div>
              {!isReplayMode && (
                <div className="text-right">
                  <span className="text-2xl font-bold text-slate-100">{blackPoints}</span>
                  <span className="text-slate-500 text-sm ml-1">pts</span>
                </div>
              )}
            </div>

            {/* Board */}
            <div className="rounded-xl overflow-hidden shadow-inner max-w-[600px] mx-auto">
              <Chessboard 
                options={{
                  position: fen,
                  darkSquareStyle: { backgroundColor: '#475569' },
                  lightSquareStyle: { backgroundColor: '#94a3b8' },
                  animationDurationInMs: 200
                }}
              />
            </div>
            
            {/* Playback Controls (Replay Only) */}
            {isReplayMode && (
              <div className="mt-6 flex justify-center items-center gap-4 bg-slate-900/50 p-4 rounded-xl border border-slate-700">
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(-1); }}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <SkipBack size={24} />
                </button>
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(p => Math.max(-1, p - 1)); }}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <ArrowLeft size={24} />
                </button>
                
                <button 
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="p-3 bg-blue-600 hover:bg-blue-500 text-white rounded-full transition-all shadow-lg"
                >
                  {isPlaying ? <Square size={24} /> : <Play size={24} className="ml-1" />}
                </button>
                
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(p => Math.min(replayMoves.length - 1, p + 1)); }}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <ArrowRight size={24} />
                </button>
                <button 
                  onClick={() => { setIsPlaying(false); setCurrentMoveIndex(replayMoves.length - 1); }}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <SkipForward size={24} />
                </button>
                <div className="ml-4 font-mono text-sm text-slate-400">
                  {currentMoveIndex + 1} / {replayMoves.length}
                </div>
              </div>
            )}
            
            {/* Debug FEN */}
            <div className="mt-2 text-center text-xs text-slate-500 font-mono break-all px-4">
              FEN: {fen}
            </div>

            {/* Player (White) Info */}
            <div className="flex justify-between items-center mt-4 px-2">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center border border-slate-300">
                  <span className="text-xl">♙</span>
                </div>
                <div>
                  <h3 className="font-bold text-slate-200">{bots.find(b => b.id === bot1)?.name || 'Loading...'}</h3>
                  <p className="text-sm text-slate-400">Playing White {matchInfo?.winner_id === bot1 && <span className="text-green-500 font-bold ml-2">(Winner)</span>}</p>
                </div>
              </div>
              {!isReplayMode && (
                <div className="text-right">
                  <span className="text-2xl font-bold text-slate-100">{whitePoints}</span>
                  <span className="text-slate-500 text-sm ml-1">pts</span>
                </div>
              )}
            </div>
            
          </div>
        </div>

        {/* Sidebar panels */}
        <div className="space-y-6">
          
          {/* Match Status */}
          <div className="bg-slate-800 p-5 rounded-2xl border border-slate-700">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2 mb-4">
              <Trophy size={18} className="text-amber-500" />
              Status
            </h3>
            <div className="p-4 bg-slate-900 rounded-xl border border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${
                  status === 'playing' ? 'bg-green-500 animate-pulse' : 
                  status === 'completed' ? 'bg-amber-500' : 
                  status === 'error' ? 'bg-red-500' : 'bg-slate-600'
                }`}></div>
                <span className="font-medium text-slate-300 capitalize">{status}</span>
              </div>
            </div>
          </div>

          {/* Move History */}
          <div className="bg-slate-800 p-5 rounded-2xl border border-slate-700 flex flex-col h-[400px]">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2 mb-4">
              <History size={18} className="text-blue-400" />
              Move History
            </h3>
            <div className="flex-1 overflow-y-auto bg-slate-900 rounded-xl p-4 border border-slate-700/50 space-y-2">
              {moveHistory.length === 0 ? (
                <div className="text-center text-slate-500 mt-10">No moves yet</div>
              ) : (
                <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                  {moveHistory.reduce((result: string[][], _, index, array) => {
                    if (index % 2 === 0) result.push(array.slice(index, index + 2));
                    return result;
                  }, []).map((pair, idx) => (
                    <React.Fragment key={idx}>
                      <div className="text-slate-400 font-mono flex items-center gap-2">
                        <span className="text-slate-600 w-6">{idx + 1}.</span> 
                        <span className={isReplayMode && currentMoveIndex === idx * 2 ? 'text-blue-400 font-bold bg-blue-900/30 px-1 rounded' : ''}>{pair[0]}</span>
                      </div>
                      <div className="text-slate-400 font-mono flex items-center">
                        {pair[1] && <span className={isReplayMode && currentMoveIndex === idx * 2 + 1 ? 'text-blue-400 font-bold bg-blue-900/30 px-1 rounded' : ''}>{pair[1]}</span>}
                      </div>
                    </React.Fragment>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          {/* AI Commentary Panel */}
          {commentary && (
            <div className="bg-slate-800 p-5 rounded-2xl border border-blue-500/50 shadow-[0_0_20px_rgba(59,130,246,0.15)] animate-in slide-in-from-right-4 duration-500 fade-in">
              <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 flex items-center gap-2 mb-3">
                <span className="text-xl">🤖</span>
                Grandmaster AI
              </h3>
              <div className="p-4 bg-slate-900 rounded-xl border border-slate-700/50">
                <p className="text-slate-300 italic font-medium">"{commentary}"</p>
              </div>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}
