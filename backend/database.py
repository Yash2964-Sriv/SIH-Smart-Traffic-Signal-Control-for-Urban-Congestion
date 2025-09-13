"""
Database connection and utilities for Smart Traffic Simulator
"""
import logging
from typing import Optional
import motor.motor_asyncio
import redis.asyncio as redis
from pymongo import MongoClient

from config.settings import settings

logger = logging.getLogger(__name__)

# Global database connections
mongodb_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
mongodb_database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
redis_client: Optional[redis.Redis] = None

# Development mode flag
DEV_MODE = True  # Set to False when databases are available


async def init_database():
    """Initialize database connections"""
    global mongodb_client, mongodb_database, redis_client, DEV_MODE
    
    if DEV_MODE:
        logger.warning("Running in development mode without databases")
        return
    
    try:
        # Initialize MongoDB connection
        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_database = mongodb_client[settings.MONGODB_DATABASE]
        
        # Test MongoDB connection
        await mongodb_client.admin.command('ping')
        logger.info("MongoDB connection established successfully")
        
        # Initialize Redis connection
        redis_client = redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        
        # Test Redis connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")
        logger.warning("Continuing in development mode without databases")
        DEV_MODE = True


async def close_database():
    """Close database connections"""
    global mongodb_client, redis_client
    
    if DEV_MODE:
        return
    
    try:
        if mongodb_client:
            mongodb_client.close()
            logger.info("MongoDB connection closed")
        
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


def get_mongodb_database():
    """Get MongoDB database instance"""
    if DEV_MODE:
        logger.warning("MongoDB not available in development mode")
        return None
    if not mongodb_database:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return mongodb_database


def get_redis_client():
    """Get Redis client instance"""
    if DEV_MODE:
        logger.warning("Redis not available in development mode")
        return None
    if not redis_client:
        raise RuntimeError("Redis not initialized. Call init_database() first.")
    return redis_client


# Database collections
def get_traffic_collection():
    """Get traffic data collection"""
    if DEV_MODE:
        return None
    return get_mongodb_database().traffic_data


def get_simulation_collection():
    """Get simulation runs collection"""
    if DEV_MODE:
        return None
    return get_mongodb_database().simulation_runs


def get_ai_models_collection():
    """Get AI models collection"""
    if DEV_MODE:
        return None
    return get_mongodb_database().ai_models


def get_camera_feeds_collection():
    """Get camera feeds collection"""
    if DEV_MODE:
        return None
    return get_mongodb_database().camera_feeds


def get_metrics_collection():
    """Get performance metrics collection"""
    if DEV_MODE:
        return None
    return get_mongodb_database().performance_metrics


def get_config_collection():
    """Get configurations collection"""
    if DEV_MODE:
        return None
    return get_mongodb_database().configurations
