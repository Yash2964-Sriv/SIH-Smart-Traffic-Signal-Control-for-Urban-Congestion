"""
Traffic data router for Smart Traffic Simulator
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from backend.database import get_traffic_collection, get_redis_client, DEV_MODE
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class TrafficData(BaseModel):
    """Traffic data model"""
    intersection_id: str
    timestamp: datetime
    lane_data: Dict[str, Dict[str, Any]]
    signal_state: Dict[str, Any]
    ai_decision: Optional[Dict[str, Any]] = None


class TrafficMetrics(BaseModel):
    """Traffic metrics model"""
    intersection_id: str
    timestamp: datetime
    total_vehicles: int
    average_wait_time: float
    queue_length: int
    throughput: float


@router.get("/")
async def get_traffic_data(
    intersection_id: str = Query(default=settings.INTERSECTION_ID),
    limit: int = Query(default=100, le=1000),
    start_time: Optional[datetime] = Query(default=None),
    end_time: Optional[datetime] = Query(default=None)
) -> List[Dict[str, Any]]:
    """Get traffic data for an intersection"""
    if DEV_MODE:
        # Return mock data for development
        return [
            {
                "intersection_id": intersection_id,
                "timestamp": datetime.now(),
                "lane_data": {
                    "north": {"queue_length": 5, "throughput": 12.5},
                    "south": {"queue_length": 3, "throughput": 15.2},
                    "east": {"queue_length": 8, "throughput": 8.7},
                    "west": {"queue_length": 2, "throughput": 18.3}
                },
                "signal_state": {
                    "north": "green",
                    "south": "red",
                    "east": "red",
                    "west": "red"
                }
            }
        ]
    
    try:
        collection = get_traffic_collection()
        
        # Build query
        query = {"intersection_id": intersection_id}
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time
        
        # Get data
        cursor = collection.find(query).sort("timestamp", -1).limit(limit)
        data = await cursor.to_list(length=limit)
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching traffic data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/")
async def create_traffic_data(data: TrafficData) -> Dict[str, Any]:
    """Create new traffic data entry"""
    if DEV_MODE:
        # Mock response for development
        return {
            "id": "mock_id_123",
            "message": "Traffic data created successfully (development mode)"
        }
    
    try:
        collection = get_traffic_collection()
        
        # Insert data
        result = await collection.insert_one(data.dict())
        
        # Publish to Redis for real-time updates
        redis_client = get_redis_client()
        if redis_client:
            await redis_client.publish(
                f"traffic:{data.intersection_id}",
                str(data.dict())
            )
        
        return {
            "id": str(result.inserted_id),
            "message": "Traffic data created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating traffic data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics")
async def get_traffic_metrics(
    intersection_id: str = Query(default=settings.INTERSECTION_ID),
    time_window: int = Query(default=3600, description="Time window in seconds")
) -> TrafficMetrics:
    """Get traffic metrics for an intersection"""
    if DEV_MODE:
        # Return mock metrics for development
        return TrafficMetrics(
            intersection_id=intersection_id,
            timestamp=datetime.now(),
            total_vehicles=45,
            average_wait_time=2.3,
            queue_length=18,
            throughput=13.7
        )
    
    try:
        collection = get_traffic_collection()
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get data for the time window
        cursor = collection.find({
            "intersection_id": intersection_id,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        })
        
        data = await cursor.to_list(length=None)
        
        if not data:
            raise HTTPException(status_code=404, detail="No traffic data found")
        
        # Calculate metrics
        total_vehicles = sum(
            sum(lane.get("throughput", 0) for lane in entry["lane_data"].values())
            for entry in data
        )
        
        wait_times = []
        queue_lengths = []
        throughputs = []
        
        for entry in data:
            for lane_data in entry["lane_data"].values():
                wait_times.append(lane_data.get("wait_time", 0))
                queue_lengths.append(lane_data.get("queue_length", 0))
                throughputs.append(lane_data.get("throughput", 0))
        
        average_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
        queue_length = sum(queue_lengths)
        throughput = sum(throughputs)
        
        return TrafficMetrics(
            intersection_id=intersection_id,
            timestamp=end_time,
            total_vehicles=total_vehicles,
            average_wait_time=average_wait_time,
            queue_length=queue_length,
            throughput=throughput
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating traffic metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/realtime")
async def get_realtime_traffic(
    intersection_id: str = Query(default=settings.INTERSECTION_ID)
) -> Dict[str, Any]:
    """Get real-time traffic data from Redis"""
    try:
        redis_client = get_redis_client()
        
        # Get latest data from Redis
        latest_data = await redis_client.get(f"traffic_latest:{intersection_id}")
        
        if not latest_data:
            raise HTTPException(status_code=404, detail="No real-time data available")
        
        return {"data": latest_data, "timestamp": datetime.utcnow()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching real-time traffic data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
