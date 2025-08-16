#!/usr/bin/env python3
"""
Setup script for the AI GTM Engine.
Handles initial configuration and database setup.
"""

import os
import sys
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_config_file():
    """Create the API keys configuration file."""
    config_example = Path("config/api_keys.yaml.example")
    config_file = Path("config/api_keys.yaml")
    
    if not config_file.exists():
        if config_example.exists():
            shutil.copy(config_example, config_file)
            print("✅ Created config/api_keys.yaml from template")
            print("⚠️  Please edit config/api_keys.yaml and add your API keys")
        else:
            print("❌ config/api_keys.yaml.example not found")
            return False
    else:
        print("✅ config/api_keys.yaml already exists")
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "data/raw",
        "data/processed", 
        "data/enriched",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")
    return True

def setup_database():
    """Initialize the database."""
    try:
        from src.core.database import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def create_env_file():
    """Create a .env file with basic configuration."""
    env_file = Path(".env")
    
    if not env_file.exists():
        env_content = """# AI GTM Engine Environment Variables

# Database (using SQLite for development)
DB_DATABASE_URL=sqlite:///./ai_gtm_engine.db

# Redis (optional - for production)
REDIS_URL=redis://localhost:6379

# Logging
APP_LOG_LEVEL=INFO
APP_DEBUG=false

# API Keys (add your actual keys here or in config/api_keys.yaml)
# API_OPENAI_API_KEY=your_openai_api_key_here
# API_ANTHROPIC_API_KEY=your_anthropic_api_key_here
# API_GITHUB_TOKEN=your_github_token_here
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with basic configuration")
    else:
        print("✅ .env file already exists")
    
    return True

def main():
    """Main setup function."""
    print("🚀 AI GTM Engine Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Create configuration files
    if not create_config_file():
        return False
    
    # Create environment file
    if not create_env_file():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit config/api_keys.yaml and add your API keys")
    print("2. Run: python start.py")
    print("3. Run: python demo.py")
    print("\n📱 Access points:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Dashboard: http://localhost:8501")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
