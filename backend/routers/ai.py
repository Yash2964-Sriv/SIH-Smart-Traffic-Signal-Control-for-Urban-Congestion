"""
AI router for Smart Traffic Simulator
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel

from backend.database import get_ai_models_collection, get_redis_client
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class AIModel(BaseModel):
    """AI model model"""
    model_id: str
    model_name: str
    model_type: str  # PPO, DQN, etc.
    version: str
    created_at: datetime
    status: str  # active, inactive, training
    parameters: Dict[str, Any]
    performance_metrics: Optional[Dict[str, Any]] = None


class AIDecision(BaseModel):
    """AI decision model"""
    intersection_id: str
    timestamp: datetime
    action: str  # extend_green, change_phase, etc.
    confidence: float
    reasoning: str
    input_data: Dict[str, Any]


@router.get("/")
async def get_ai_models(
    model_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200)
) -> List[Dict[str, Any]]:
    """Get AI models"""
    try:
        collection = get_ai_models_collection()
        
        # Build query
        query = {}
        if model_type:
            query["model_type"] = model_type
        if status:
            query["status"] = status
        
        # Get data
        cursor = collection.find(query).sort("created_at", -1).limit(limit)
        data = await cursor.to_list(length=limit)
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching AI models: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/")
async def create_ai_model(model: AIModel) -> Dict[str, Any]:
    """Create new AI model"""
    try:
        collection = get_ai_models_collection()
        
        # Insert model
        result = await collection.insert_one(model.dict())
        
        return {
            "model_id": model.model_id,
            "message": "AI model created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating AI model: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{model_id}")
async def get_ai_model(model_id: str) -> Dict[str, Any]:
    """Get specific AI model"""
    try:
        collection = get_ai_models_collection()
        
        # Get model
        model = await collection.find_one({"model_id": model_id})
        
        if not model:
            raise HTTPException(status_code=404, detail="AI model not found")
        
        return model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching AI model: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{model_id}/activate")
async def activate_ai_model(model_id: str) -> Dict[str, Any]:
    """Activate an AI model"""
    try:
        collection = get_ai_models_collection()
        
        # Update model status
        result = await collection.update_one(
            {"model_id": model_id},
            {"$set": {"status": "active"}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="AI model not found")
        
        # Publish to Redis for AI controller
        redis_client = get_redis_client()
        await redis_client.publish(
            "ai:activate",
            model_id
        )
        
        return {
            "model_id": model_id,
            "message": "AI model activated successfully",
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating AI model: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{model_id}/deactivate")
async def deactivate_ai_model(model_id: str) -> Dict[str, Any]:
    """Deactivate an AI model"""
    try:
        collection = get_ai_models_collection()
        
        # Update model status
        result = await collection.update_one(
            {"model_id": model_id},
            {"$set": {"status": "inactive"}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="AI model not found")
        
        # Publish to Redis for AI controller
        redis_client = get_redis_client()
        await redis_client.publish(
            "ai:deactivate",
            model_id
        )
        
        return {
            "model_id": model_id,
            "message": "AI model deactivated successfully",
            "status": "inactive"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating AI model: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/decision")
async def make_ai_decision(decision: AIDecision) -> Dict[str, Any]:
    """Make an AI decision"""
    try:
        # Publish decision to Redis for AI controller
        redis_client = get_redis_client()
        await redis_client.publish(
            f"ai:decision:{decision.intersection_id}",
            str(decision.dict())
        )
        
        return {
            "intersection_id": decision.intersection_id,
            "action": decision.action,
            "confidence": decision.confidence,
            "timestamp": decision.timestamp,
            "message": "AI decision sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error making AI decision: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/current")
async def get_current_ai_status() -> Dict[str, Any]:
    """Get current AI status"""
    try:
        collection = get_ai_models_collection()
        
        # Get active model
        active_model = await collection.find_one({"status": "active"})
        
        if not active_model:
            return {"status": "inactive", "message": "No active AI model"}
        
        return {
            "status": "active",
            "model_id": active_model["model_id"],
            "model_name": active_model["model_name"],
            "model_type": active_model["model_type"],
            "version": active_model["version"]
        }
        
    except Exception as e:
        logger.error(f"Error fetching current AI status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload")
async def upload_model_file(
    file: UploadFile = File(...),
    model_id: str = Query(...),
    model_type: str = Query(...)
) -> Dict[str, Any]:
    """Upload AI model file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.pth', '.pt', '.h5', '.pb')):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Save file
        file_path = f"{settings.MODELS_DIR}/{model_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update model in database
        collection = get_ai_models_collection()
        await collection.update_one(
            {"model_id": model_id},
            {
                "$set": {
                    "file_path": file_path,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "model_id": model_id,
            "file_path": file_path,
            "message": "Model file uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading model file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
