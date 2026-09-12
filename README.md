# AI Chess Bot Arena

An AI-powered platform for running, watching, analyzing and comparing autonomous chess bots through live matches and knockout tournaments.

## Features

- Autonomous bot-vs-bot matches
- UCI/FEN-based chess engine integration
- Live chessboard
- Game replay
- Knockout tournaments
- Bot registration/upload
- Tournament bracket
- Stockfish analysis
- Gemini-powered explanations
- AI analytics dashboard
- Bot performance statistics
- Game history

## Architecture

```text
React + TypeScript
        ↓
FastAPI
        ↓
Chess Game Engine
        ↓
Bot Processes

Completed Game
      ↓
Stockfish
      ↓
Structured Analysis
      ↓
Gemini
      ↓
Natural Language Explanation
```

## Project Structure

- `Engine/` - Core Python chess engine that runs matches in isolated processes.
- `Frontend/` - React and TypeScript SPA for interacting with the arena.
- `Server/` - FastAPI backend for managing bots, tournaments, and history.
- `bots/` - Sample and system bots used for testing.
- `participant_bots/` - Upload directory for participant Python bots.

## How It Works

One complete match flows as follows:

```text
Bot A
 ↓
Bot B
 ↓
game.py
 ↓
Move generation
 ↓
Game result
 ↓
Stored game
 ↓
Stockfish
 ↓
Gemini
 ↓
Replay + AI Review + Dashboard
```

## Tournament Architecture

```text
Registration
 ↓
Seeding
 ↓
Knockout bracket
 ↓
Match queue
 ↓
Game execution
 ↓
Winner advancement
 ↓
Final
```

## AI Analysis

- **Stockfish**: Provides objective chess evaluation (centipawn loss, blunders, mistakes).
- **Gemini**: Provides a human-readable explanation for critical evaluation swings.

*Note: Gemini does NOT determine the chess evaluation. It only explains the numerical data produced by Stockfish.*

## Setup

### Requirements

- Python 3.10+
- Node.js 18+ (npm/yarn/pnpm)
- Stockfish installed locally
- Gemini API key

### Environment Variables

Copy `.env.example` to `.env` in the root directory:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.6-flash
# STOCKFISH_PATH=/path/to/stockfish
```

*Note: NEVER commit your actual `.env` file.*

### Backend Setup

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn Server.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd Frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Development Phases

This project was developed incrementally through the following logical phases:

1. **Phase 01 — Repository and engine foundation**
2. **Phase 02 — Bot execution and UCI integration**
3. **Phase 03 — Backend game orchestration**
4. **Phase 04 — Frontend application shell**
5. **Phase 05 — Live match interface**
6. **Phase 06 — Game replay system**
7. **Phase 07 — Tournament system**
8. **Phase 08 — Knockout tournament architecture**
9. **Phase 09 — Stockfish analysis**
10. **Phase 10 — Gemini AI review**
11. **Phase 11 — Analytics dashboard**
12. **Phase 12 — Security and production cleanup**
13. **Phase 13 — Documentation and portfolio release**