"""
Metrics router for Smart Traffic Simulator
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.database import get_metrics_collection, get_traffic_collection
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    run_id: str
    intersection_id: str
    timestamp: datetime
    metrics: Dict[str, Any]
    comparison: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_performance_metrics(
    intersection_id: Optional[str] = Query(default=None),
    run_id: Optional[str] = Query(default=None),
    start_time: Optional[datetime] = Query(default=None),
    end_time: Optional[datetime] = Query(default=None),
    limit: int = Query(default=100, le=1000)
) -> List[Dict[str, Any]]:
    """Get performance metrics"""
    try:
        collection = get_metrics_collection()
        
        # Build query
        query = {}
        if intersection_id:
            query["intersection_id"] = intersection_id
        if run_id:
            query["run_id"] = run_id
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
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary")
async def get_metrics_summary(
    intersection_id: str = Query(default=settings.INTERSECTION_ID),
    time_window: int = Query(default=3600, description="Time window in seconds")
) -> Dict[str, Any]:
    """Get metrics summary for an intersection"""
    try:
        collection = get_metrics_collection()
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get metrics for the time window
        cursor = collection.find({
            "intersection_id": intersection_id,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        })
        
        data = await cursor.to_list(length=None)
        
        if not data:
            return {
                "intersection_id": intersection_id,
                "time_window": time_window,
                "message": "No metrics data available"
            }
        
        # Calculate summary statistics
        total_runs = len(data)
        avg_wait_time = 0
        avg_queue_length = 0
        total_throughput = 0
        efficiency_improvement = 0
        
        for entry in data:
            metrics = entry.get("metrics", {})
            avg_wait_time += metrics.get("average_wait_time", 0)
            avg_queue_length += metrics.get("queue_length", 0)
            total_throughput += metrics.get("throughput", 0)
            
            comparison = entry.get("comparison", {})
            efficiency_improvement += comparison.get("efficiency_improvement", 0)
        
        avg_wait_time /= total_runs if total_runs > 0 else 1
        avg_queue_length /= total_runs if total_runs > 0 else 1
        efficiency_improvement /= total_runs if total_runs > 0 else 1
        
        return {
            "intersection_id": intersection_id,
            "time_window": time_window,
            "total_runs": total_runs,
            "average_wait_time": round(avg_wait_time, 2),
            "average_queue_length": round(avg_queue_length, 2),
            "total_throughput": total_throughput,
            "efficiency_improvement": round(efficiency_improvement, 2),
            "timestamp": end_time
        }
        
    except Exception as e:
        logger.error(f"Error calculating metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/comparison")
async def get_performance_comparison(
    intersection_id: str = Query(default=settings.INTERSECTION_ID),
    time_window: int = Query(default=3600, description="Time window in seconds")
) -> Dict[str, Any]:
    """Get performance comparison between AI and traditional control"""
    try:
        collection = get_metrics_collection()
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get metrics for the time window
        cursor = collection.find({
            "intersection_id": intersection_id,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        })
        
        data = await cursor.to_list(length=None)
        
        if not data:
            return {
                "intersection_id": intersection_id,
                "time_window": time_window,
                "message": "No comparison data available"
            }
        
        # Calculate comparison statistics
        ai_wait_times = []
        traditional_wait_times = []
        ai_queue_lengths = []
        traditional_queue_lengths = []
        ai_throughputs = []
        traditional_throughputs = []
        
        for entry in data:
            comparison = entry.get("comparison", {})
            ai_wait_times.append(comparison.get("ai_wait_time", 0))
            traditional_wait_times.append(comparison.get("traditional_wait_time", 0))
            ai_queue_lengths.append(comparison.get("ai_queue_length", 0))
            traditional_queue_lengths.append(comparison.get("traditional_queue_length", 0))
            ai_throughputs.append(comparison.get("ai_throughput", 0))
            traditional_throughputs.append(comparison.get("traditional_throughput", 0))
        
        # Calculate averages
        avg_ai_wait_time = sum(ai_wait_times) / len(ai_wait_times) if ai_wait_times else 0
        avg_traditional_wait_time = sum(traditional_wait_times) / len(traditional_wait_times) if traditional_wait_times else 0
        avg_ai_queue_length = sum(ai_queue_lengths) / len(ai_queue_lengths) if ai_queue_lengths else 0
        avg_traditional_queue_length = sum(traditional_queue_lengths) / len(traditional_queue_lengths) if traditional_queue_lengths else 0
        avg_ai_throughput = sum(ai_throughputs) / len(ai_throughputs) if ai_throughputs else 0
        avg_traditional_throughput = sum(traditional_throughputs) / len(traditional_throughputs) if traditional_throughputs else 0
        
        # Calculate improvements
        wait_time_improvement = ((avg_traditional_wait_time - avg_ai_wait_time) / avg_traditional_wait_time * 100) if avg_traditional_wait_time > 0 else 0
        queue_length_improvement = ((avg_traditional_queue_length - avg_ai_queue_length) / avg_traditional_queue_length * 100) if avg_traditional_queue_length > 0 else 0
        throughput_improvement = ((avg_ai_throughput - avg_traditional_throughput) / avg_traditional_throughput * 100) if avg_traditional_throughput > 0 else 0
        
        return {
            "intersection_id": intersection_id,
            "time_window": time_window,
            "ai_performance": {
                "average_wait_time": round(avg_ai_wait_time, 2),
                "average_queue_length": round(avg_ai_queue_length, 2),
                "average_throughput": round(avg_ai_throughput, 2)
            },
            "traditional_performance": {
                "average_wait_time": round(avg_traditional_wait_time, 2),
                "average_queue_length": round(avg_traditional_queue_length, 2),
                "average_throughput": round(avg_traditional_throughput, 2)
            },
            "improvements": {
                "wait_time_improvement": round(wait_time_improvement, 2),
                "queue_length_improvement": round(queue_length_improvement, 2),
                "throughput_improvement": round(throughput_improvement, 2)
            },
            "timestamp": end_time
        }
        
    except Exception as e:
        logger.error(f"Error calculating performance comparison: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trends")
async def get_metrics_trends(
    intersection_id: str = Query(default=settings.INTERSECTION_ID),
    metric: str = Query(default="wait_time", description="Metric to analyze"),
    time_window: int = Query(default=86400, description="Time window in seconds")
) -> Dict[str, Any]:
    """Get metrics trends over time"""
    try:
        collection = get_metrics_collection()
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get metrics for the time window
        cursor = collection.find({
            "intersection_id": intersection_id,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }).sort("timestamp", 1)
        
        data = await cursor.to_list(length=None)
        
        if not data:
            return {
                "intersection_id": intersection_id,
                "metric": metric,
                "time_window": time_window,
                "message": "No trend data available"
            }
        
        # Extract trend data
        timestamps = []
        values = []
        
        for entry in data:
            timestamps.append(entry["timestamp"].isoformat())
            
            if metric == "wait_time":
                values.append(entry.get("metrics", {}).get("average_wait_time", 0))
            elif metric == "queue_length":
                values.append(entry.get("metrics", {}).get("queue_length", 0))
            elif metric == "throughput":
                values.append(entry.get("metrics", {}).get("throughput", 0))
            elif metric == "efficiency":
                values.append(entry.get("comparison", {}).get("efficiency_improvement", 0))
            else:
                values.append(0)
        
        return {
            "intersection_id": intersection_id,
            "metric": metric,
            "time_window": time_window,
            "timestamps": timestamps,
            "values": values,
            "data_points": len(timestamps)
        }
        
    except Exception as e:
        logger.error(f"Error calculating metrics trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
