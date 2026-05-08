#!/bin/bash
# Quick start script for ContextBridge

set -e

echo "🚀 ContextBridge - Day 1 Setup"
echo "================================"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python --version)"
echo ""

# Create virtual environment
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"
echo ""

# Create data directory
mkdir -p data
echo "✅ Data directory created"
echo ""

echo "🎯 Ready to run ContextBridge!"
echo ""
echo "To start the server:"
echo "  python main.py"
echo ""
echo "Then visit:"
echo "  http://localhost:8000/docs"
echo ""
echo "To index the example content:"
echo "  curl -X POST \"http://localhost:8000/api/v1/index/file\" \\"
echo "    -H \"Content-Type: application/x-www-form-urlencoded\" \\"
echo "    -d \"file_path=$(pwd)/example_content.md\""
echo ""
