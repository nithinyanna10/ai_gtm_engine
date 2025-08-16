#!/usr/bin/env python3
"""
Startup script for the AI GTM Engine.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import streamlit
        import openai
        import anthropic
        import sqlalchemy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_config():
    """Check if configuration files exist."""
    config_file = Path("config/api_keys.yaml")
    if not config_file.exists():
        print("⚠️  Configuration file not found")
        print("Please copy config/api_keys.yaml.example to config/api_keys.yaml")
        print("and add your API keys")
        return False
    print("✅ Configuration file found")
    return True

def start_api_server():
    """Start the FastAPI server."""
    print("🚀 Starting API server...")
    try:
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        print("✅ API server started on http://localhost:8000")
        return True
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return False

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("📊 Starting dashboard...")
    try:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", 
            "run", "src/monitoring/dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        print("✅ Dashboard started on http://localhost:8501")
        return True
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return False

def initialize_database():
    """Initialize database without sample data."""
    print("🗄️ Initializing database...")
    
    try:
        from src.core.database import init_db
        
        # Initialize database
        init_db()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")

def main():
    """Main startup function."""
    print("🚀 AI GTM Engine Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check configuration
    if not check_config():
        print("\nYou can still start the engine, but some features may not work without API keys.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Initialize database
    initialize_database()
    
    # Start services
    api_started = start_api_server()
    dashboard_started = start_dashboard()
    
    if api_started and dashboard_started:
        print("\n🎉 AI GTM Engine is running!")
        print("\n📱 Access points:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Dashboard: http://localhost:8501")
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down AI GTM Engine...")
            print("✅ Services stopped")
    else:
        print("❌ Failed to start some services")

if __name__ == "__main__":
    main()
