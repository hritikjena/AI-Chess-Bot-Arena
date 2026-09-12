# VPS Deployment Guide

This guide explains how to deploy the **AI Chess Bot Arena** to a Virtual Private Server (VPS) such as DigitalOcean, AWS EC2, or Linode using Docker.

## Prerequisites
- A VPS running Ubuntu (or your preferred Linux distribution)
- Docker and Docker Compose installed on the VPS
- Your Gemini API Key

## 1. Clone the Repository on your VPS

SSH into your VPS and clone the repository:

```bash
git clone https://github.com/hritikjena/AI-Chess-Bot-Arena.git
cd AI-Chess-Bot-Arena
```

## 2. Configure Environment Variables

The backend needs your Gemini API key, and the frontend needs to know the public IP address (or domain name) of your VPS so it can talk to the backend.

### Backend Config
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` (using `nano .env`) and add your real key:
```env
GEMINI_API_KEY=your_real_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
STOCKFISH_PATH=/usr/games/stockfish
```

### Frontend Config
By default, the `docker-compose.yml` builds the frontend assuming the backend is at `http://localhost:8000`. **You must change this to your VPS's public IP or Domain name**.

Open `docker-compose.yml` and modify the `args` under the `frontend` service:

```yaml
    frontend:
      build:
        context: ./Frontend
        dockerfile: Dockerfile
        args:
          - VITE_API_BASE_URL=http://<YOUR-VPS-IP>:8000/api
          - VITE_WS_BASE_URL=ws://<YOUR-VPS-IP>:8000/api
```
*(Replace `<YOUR-VPS-IP>` with your actual server IP, e.g., `123.45.67.89`)*

## 3. Build and Start the Containers

Run the following command to build the Docker images and start the containers in detached mode:

```bash
docker compose up -d --build
```

## 4. Access the Application

Once the containers are running, you can access your application by navigating to your server's IP address in a web browser:

- **Frontend**: `http://<YOUR-VPS-IP>`
- **Backend API Docs**: `http://<YOUR-VPS-IP>:8000/docs`

## Updating the Application

When you push new changes to GitHub and want to update your VPS:

```bash
# Pull the latest changes
git pull origin main

# Rebuild and restart the containers
docker compose up -d --build
```
