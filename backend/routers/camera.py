"""
Camera router for Smart Traffic Simulator
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel

from backend.database import get_camera_feeds_collection, get_redis_client
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class CameraFeed(BaseModel):
    """Camera feed model"""
    camera_id: str
    intersection_id: str
    timestamp: datetime
    feed_url: str
    status: str  # active, inactive, processing
    metadata: Dict[str, Any] = {}


class VehicleDetection(BaseModel):
    """Vehicle detection model"""
    camera_id: str
    timestamp: datetime
    vehicles: List[Dict[str, Any]]
    lane_counts: Dict[str, int]
    confidence: float


@router.get("/")
async def get_camera_feeds(
    intersection_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200)
) -> List[Dict[str, Any]]:
    """Get camera feeds"""
    try:
        collection = get_camera_feeds_collection()
        
        # Build query
        query = {}
        if intersection_id:
            query["intersection_id"] = intersection_id
        if status:
            query["status"] = status
        
        # Get data
        cursor = collection.find(query).sort("timestamp", -1).limit(limit)
        data = await cursor.to_list(length=limit)
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching camera feeds: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/")
async def create_camera_feed(feed: CameraFeed) -> Dict[str, Any]:
    """Create new camera feed"""
    try:
        collection = get_camera_feeds_collection()
        
        # Insert feed
        result = await collection.insert_one(feed.dict())
        
        # Publish to Redis for camera integration
        redis_client = get_redis_client()
        await redis_client.publish(
            "camera:new_feed",
            str(feed.dict())
        )
        
        return {
            "camera_id": feed.camera_id,
            "message": "Camera feed created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating camera feed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{camera_id}")
async def get_camera_feed(camera_id: str) -> Dict[str, Any]:
    """Get specific camera feed"""
    try:
        collection = get_camera_feeds_collection()
        
        # Get feed
        feed = await collection.find_one({"camera_id": camera_id})
        
        if not feed:
            raise HTTPException(status_code=404, detail="Camera feed not found")
        
        return feed
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching camera feed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{camera_id}/status")
async def update_camera_status(
    camera_id: str,
    status: str = Query(..., description="New status")
) -> Dict[str, Any]:
    """Update camera feed status"""
    try:
        collection = get_camera_feeds_collection()
        
        # Update status
        result = await collection.update_one(
            {"camera_id": camera_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Camera feed not found")
        
        # Publish to Redis
        redis_client = get_redis_client()
        await redis_client.publish(
            f"camera:status:{camera_id}",
            status
        )
        
        return {
            "camera_id": camera_id,
            "status": status,
            "message": "Camera status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating camera status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/detection")
async def process_vehicle_detection(detection: VehicleDetection) -> Dict[str, Any]:
    """Process vehicle detection from camera feed"""
    try:
        # Publish detection to Redis for processing
        redis_client = get_redis_client()
        await redis_client.publish(
            f"camera:detection:{detection.camera_id}",
            str(detection.dict())
        )
        
        return {
            "camera_id": detection.camera_id,
            "vehicles_detected": len(detection.vehicles),
            "timestamp": detection.timestamp,
            "message": "Vehicle detection processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing vehicle detection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stream/{camera_id}")
async def get_camera_stream(camera_id: str) -> Dict[str, Any]:
    """Get camera stream URL"""
    try:
        collection = get_camera_feeds_collection()
        
        # Get camera feed
        feed = await collection.find_one({"camera_id": camera_id})
        
        if not feed:
            raise HTTPException(status_code=404, detail="Camera feed not found")
        
        if feed["status"] != "active":
            raise HTTPException(status_code=400, detail="Camera feed is not active")
        
        return {
            "camera_id": camera_id,
            "stream_url": feed["feed_url"],
            "status": feed["status"],
            "metadata": feed.get("metadata", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching camera stream: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload")
async def upload_camera_config(
    file: UploadFile = File(...),
    camera_id: str = Query(...),
    config_type: str = Query(..., description="Configuration type: calibration, mapping, etc.")
) -> Dict[str, Any]:
    """Upload camera configuration file"""
    try:
        # Validate file type
        allowed_types = ['.json', '.yaml', '.yml', '.xml', '.txt']
        if not any(file.filename.endswith(ext) for ext in allowed_types):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Save file
        file_path = f"{settings.DATA_DIR}/camera_configs/{camera_id}_{config_type}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update camera feed metadata
        collection = get_camera_feeds_collection()
        await collection.update_one(
            {"camera_id": camera_id},
            {
                "$set": {
                    f"metadata.{config_type}_config": file_path,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "camera_id": camera_id,
            "config_type": config_type,
            "file_path": file_path,
            "message": "Camera configuration uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading camera configuration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/active")
async def get_active_cameras() -> List[Dict[str, Any]]:
    """Get all active camera feeds"""
    try:
        collection = get_camera_feeds_collection()
        
        # Get active feeds
        cursor = collection.find({"status": "active"})
        feeds = await cursor.to_list(length=None)
        
        return [
            {
                "camera_id": feed["camera_id"],
                "intersection_id": feed["intersection_id"],
                "feed_url": feed["feed_url"],
                "timestamp": feed["timestamp"]
            }
            for feed in feeds
        ]
        
    except Exception as e:
        logger.error(f"Error fetching active cameras: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
