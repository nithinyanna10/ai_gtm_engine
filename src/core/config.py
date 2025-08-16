"""
Configuration management for the AI GTM Engine.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    database_url: str = Field(default="sqlite:///./ai_gtm_engine.db")
    echo: bool = Field(default=False)
    
    class Config:
        env_prefix = "DB_"

class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    redis_url: str = Field(default="redis://localhost:6379")
    
    class Config:
        env_prefix = "REDIS_"

class APISettings(BaseSettings):
    """API configuration settings."""
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None)
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")
    
    # GitHub
    github_token: Optional[str] = Field(default=None)
    
    # Reddit
    reddit_client_id: Optional[str] = Field(default=None)
    reddit_client_secret: Optional[str] = Field(default=None)
    reddit_user_agent: str = Field(default="AI_GTM_Engine/1.0")
    
    # LinkedIn
    linkedin_username: Optional[str] = Field(default=None)
    linkedin_password: Optional[str] = Field(default=None)
    
    # Email Services (Free alternatives to SendGrid)
    mailgun_api_key: Optional[str] = Field(default=None)
    mailgun_domain: Optional[str] = Field(default=None)
    resend_api_key: Optional[str] = Field(default=None)
    brevo_api_key: Optional[str] = Field(default=None)
    
    # SendGrid (No longer free)
    # sendgrid_api_key: Optional[str] = Field(default=None)
    
    # Twilio
    twilio_account_sid: Optional[str] = Field(default=None)
    twilio_auth_token: Optional[str] = Field(default=None)
    
    # Synthesia
    synthesia_api_key: Optional[str] = Field(default=None)
    
    # Clearbit
    clearbit_api_key: Optional[str] = Field(default=None)
    
    # BuiltWith
    builtwith_api_key: Optional[str] = Field(default=None)
    
    # Logo.dev (Company Intelligence)
    logo_dev_api_key: Optional[str] = Field(default=None)
    
    # Wappalyzer (Tech Stack) - Not free, using built-in analyzer
    # wappalyzer_api_key: Optional[str] = Field(default=None)
    
    # News API
    news_api_key: Optional[str] = Field(default=None)
    
    # Slack
    slack_webhook_url: Optional[str] = Field(default=None)
    
    class Config:
        env_prefix = "API_"

class ScoringSettings(BaseSettings):
    """Scoring algorithm configuration."""
    # Weights for different signal types
    github_weight: float = Field(default=0.25)
    community_weight: float = Field(default=0.20)
    job_posting_weight: float = Field(default=0.20)
    news_weight: float = Field(default=0.15)
    technographic_weight: float = Field(default=0.10)
    firmographic_weight: float = Field(default=0.10)
    
    # Thresholds
    high_intent_threshold: float = Field(default=0.7)
    medium_intent_threshold: float = Field(default=0.5)
    
    # Time windows (in days)
    recent_activity_window: int = Field(default=30)
    trigger_freshness_window: int = Field(default=7)
    
    class Config:
        env_prefix = "SCORING_"

class Settings(BaseSettings):
    """Main application settings."""
    app_name: str = Field(default="AI GTM Engine")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()
    scoring: ScoringSettings = ScoringSettings()
    
    # File paths
    base_dir: Path = Path(__file__).parent.parent.parent
    config_dir: Path = base_dir / "config"
    data_dir: Path = base_dir / "data"
    
    class Config:
        env_prefix = "APP_"

# Global settings instance
settings = Settings()

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_file = settings.config_dir / file_path
    if config_file.exists():
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    return {}

def save_yaml_config(file_path: str, config: Dict[str, Any]) -> None:
    """Save configuration to YAML file."""
    config_file = settings.config_dir / file_path
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

# Load API keys from YAML if not set in environment
def load_api_keys():
    """Load API keys from YAML configuration."""
    api_config = load_yaml_config("api_keys.yaml")
    
    # Only set if not already set in environment
    for key, value in api_config.items():
        env_key = f"API_{key.upper()}"
        if not os.getenv(env_key) and value:
            os.environ[env_key] = str(value)

# Initialize API keys
load_api_keys()

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
