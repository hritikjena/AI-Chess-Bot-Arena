# Deployment Guide (Vercel & Render)

This guide explains how to deploy the **AI Chess Bot Arena** with **$0 upfront cost** using Vercel (Frontend) and Render (Backend).

## 1. Backend Deployment (Render)

Render will host the FastAPI backend, WebSocket server, and execute the Python engine logic.

1. **Create a Render Account**: Go to [render.com](https://render.com) and sign up.
2. **Create a Web Service**: Click "New +" -> "Web Service".
3. **Connect Repository**: Connect your GitHub account and select the `AI-Chess-Bot-Arena` repository.
4. **Configure the Service**:
   - **Name**: `chess-bot-arena-api` (or similar)
   - **Environment**: `Python`
   - **Build Command**: `./render-build.sh`
   - **Start Command**: `uvicorn Server.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. **Environment Variables**:
   Under "Advanced", add the following environment variables:
   - `GEMINI_API_KEY`: Your real Google Gemini API Key.
   - `GEMINI_MODEL`: `gemini-3.6-flash` (or your preferred model).
   - `STOCKFISH_PATH`: `./stockfish-ubuntu`
6. **Deploy**: Click "Create Web Service". Render will run `render-build.sh` (which installs Python dependencies and downloads the Stockfish binary) and then start the Uvicorn server.
7. **Get the URL**: Once deployed, copy your Render URL (e.g., `https://chess-bot-arena-api.onrender.com`). Verify it works by visiting the `/health` endpoint.

> **Note on Persistence**: The Render Free Tier spins down after 15 minutes of inactivity. When it spins down, any SQLite database files or custom uploaded bots are lost. For permanent data persistence, you should upgrade to a persistent disk (Render paid feature) or migrate the database URL to an external PostgreSQL provider (like Supabase).

---

## 2. Frontend Deployment (Vercel)

Vercel will host the React + Vite frontend.

1. **Create a Vercel Account**: Go to [vercel.com](https://vercel.com) and sign up.
2. **Create a New Project**: Click "Add New..." -> "Project".
3. **Import Repository**: Connect your GitHub account and import the `AI-Chess-Bot-Arena` repository.
4. **Configure Project**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `Frontend` (Click Edit to select the Frontend folder)
5. **Environment Variables**:
   Open the "Environment Variables" section and add the endpoints for your deployed Render backend:
   - `VITE_API_BASE_URL`: `https://your-render-app-url.onrender.com/api`
   - `VITE_WS_BASE_URL`: `wss://your-render-app-url.onrender.com/api`
   *(Make sure to use `wss://` for secure WebSockets!)*
6. **Deploy**: Click "Deploy". Vercel will run `npm run build` and publish your frontend.
7. **Visit your Site**: Your AI Chess Bot Arena is now live!

## 3. Updating the Application

When you push new changes to the `main` branch of your GitHub repository:
- **Vercel** will automatically trigger a build and update the frontend.
- **Render** will automatically trigger a build and update the backend (if auto-deploy is enabled).
