#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download stockfish if not exists
if [ ! -f "stockfish-ubuntu" ]; then
    echo "Downloading Stockfish..."
    curl -L -o stockfish.tar.gz https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-linux-x86-64-universal.tar.gz
    tar -xvf stockfish.tar.gz
    mv stockfish/stockfish-linux-x86-64-universal ./stockfish-ubuntu
    chmod +x ./stockfish-ubuntu
    rm -rf stockfish stockfish.tar.gz
fi
