#!/bin/bash
set -e

echo "🚀 Setup successfully created!"

# streamlit run academic/src/app.py --server.port=8501 --server.address=0.0.0.0 &

exec tail -f /dev/null