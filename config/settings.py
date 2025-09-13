"""
Configuration settings for Smart Traffic Simulator
"""
import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Smart Traffic Simulator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    MONGODB_DATABASE: str = Field(default="traffic_simulator", env="MONGODB_DATABASE")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # AI Configuration
    AI_MODEL_TYPE: str = Field(default="PPO", env="AI_MODEL_TYPE")
    AI_LEARNING_RATE: float = Field(default=0.0003, env="AI_LEARNING_RATE")
    AI_BATCH_SIZE: int = Field(default=64, env="AI_BATCH_SIZE")
    AI_UPDATE_FREQUENCY: int = Field(default=1000, env="AI_UPDATE_FREQUENCY")
    
    # SUMO Configuration
    SUMO_HOME: str = Field(default="/usr/share/sumo", env="SUMO_HOME")
    SUMO_CONFIG_FILE: str = Field(default="intersection.sumocfg", env="SUMO_CONFIG_FILE")
    SUMO_GUI: bool = Field(default=False, env="SUMO_GUI")
    SUMO_PORT: int = Field(default=8813, env="SUMO_PORT")
    
    # Camera Configuration
    CAMERA_FPS: int = Field(default=30, env="CAMERA_FPS")
    CAMERA_RESOLUTION: str = Field(default="1920x1080", env="CAMERA_RESOLUTION")
    CAMERA_DETECTION_CONFIDENCE: float = Field(default=0.5, env="CAMERA_DETECTION_CONFIDENCE")
    CAMERA_MODEL_PATH: str = Field(default="models/yolov8n.pt", env="CAMERA_MODEL_PATH")
    
    # Intersection Configuration
    INTERSECTION_ID: str = Field(default="main_intersection", env="INTERSECTION_ID")
    NUM_LANES: int = Field(default=4, env="NUM_LANES")
    SIGNAL_PHASES: List[Dict[str, Any]] = Field(default=[
        {
            "phase_id": "NS",
            "name": "North-South",
            "duration": 30,
            "lanes": ["north_1", "north_2", "south_1", "south_2"]
        },
        {
            "phase_id": "EW",
            "name": "East-West",
            "duration": 30,
            "lanes": ["east_1", "east_2", "west_1", "west_2"]
        }
    ])
    YELLOW_DURATION: int = Field(default=3, env="YELLOW_DURATION")
    RED_DURATION: int = Field(default=2, env="RED_DURATION")
    
    # Performance Metrics
    METRICS_UPDATE_INTERVAL: int = Field(default=5, env="METRICS_UPDATE_INTERVAL")
    METRICS_RETENTION_DAYS: int = Field(default=30, env="METRICS_RETENTION_DAYS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # File Paths
    DATA_DIR: str = Field(default="data", env="DATA_DIR")
    MODELS_DIR: str = Field(default="data/models", env="MODELS_DIR")
    LOGS_DIR: str = Field(default="logs", env="LOGS_DIR")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)
