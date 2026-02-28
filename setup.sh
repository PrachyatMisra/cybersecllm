# setup.sh - Complete Setup Script
#!/bin/bash

echo "🚀 Setting up Cybersecurity Knowledge Graph System"

# Pull Ollama models
echo "📥 Downloading LLM models..."
ollama pull llama3
ollama pull qwen

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for Neo4j
echo "⏳ Waiting for Neo4j..."
sleep 20

# Run Streamlit app
echo "🎨 Starting Streamlit application..."
streamlit run main_app.py

echo "✅ Setup complete! Access the app at http://localhost:8501"
