#!/bin/bash

set -e

echo "⚙️ Starting the Setup..."

echo "🔓 Giving Permissions to entrypoint.sh & setup.sh..."
chmod +x ./entrypoint.sh

echo "⬆️ Upping the Docker Images..."
cd .. ; docker compose up --build -d

echo "⏳ Waiting for the Ollama container to be ready..."

sleep 5 

echo "📥 Verifying and downloading the bge-m3 embedding model (this may take time on the first run)..."
docker exec ollama ollama pull bge-m3

echo "📥 Verifying and downloading the qwen3.5:2b chat model (this may take time on the first run)..."
docker exec ollama ollama pull qwen3.5:2b

echo "✅ All done! Have fun."