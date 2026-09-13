#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download stockfish if not exists
if [ ! -f "stockfish-ubuntu" ]; then
    echo "Downloading Stockfish..."
    curl -L -o stockfish.tar https://github.com/official-stockfish/Stockfish/releases/download/sf_16.1/stockfish-ubuntu-x86-64-avx2.tar
    tar -xvf stockfish.tar
    mv stockfish/stockfish-ubuntu-x86-64-avx2 ./stockfish-ubuntu
    chmod +x ./stockfish-ubuntu
    rm -rf stockfish stockfish.tar
fi
