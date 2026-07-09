#!/bin/bash
set -e

echo "Initializing the entrypoint script..."

streamlit run academic/src/interface/app.py --server.port=8501 --server.address=0.0.0.0

echo "🚀 Setup successfully created!"