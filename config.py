# config.py - Enhanced Configuration
"""
Configuration Management
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"
    
    # LLM Configuration
    ollama_endpoint: str = "http://localhost:11434"
    default_llm_model: str = "llama3"
    llm_temperature: float = 0.1
    
    # API Keys (optional)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Application Settings
    app_name: str = "CyberGraph Intelligence"
    debug_mode: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
