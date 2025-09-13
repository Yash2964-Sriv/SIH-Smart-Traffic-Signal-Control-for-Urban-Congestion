"""
Simulation router for Smart Traffic Simulator
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.database import get_simulation_collection, get_redis_client
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class SimulationConfig(BaseModel):
    """Simulation configuration model"""
    intersection_id: str
    duration: int  # Simulation duration in seconds
    traffic_density: float  # Traffic density (0.0 to 1.0)
    ai_enabled: bool = True
    parameters: Dict[str, Any] = {}


class SimulationRun(BaseModel):
    """Simulation run model"""
    run_id: str
    intersection_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str  # running, completed, failed
    config: SimulationConfig
    results: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_simulation_runs(
    intersection_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200)
) -> List[Dict[str, Any]]:
    """Get simulation runs"""
    try:
        collection = get_simulation_collection()
        
        # Build query
        query = {}
        if intersection_id:
            query["intersection_id"] = intersection_id
        if status:
            query["status"] = status
        
        # Get data
        cursor = collection.find(query).sort("start_time", -1).limit(limit)
        data = await cursor.to_list(length=limit)
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching simulation runs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/start")
async def start_simulation(config: SimulationConfig) -> Dict[str, Any]:
    """Start a new simulation"""
    try:
        collection = get_simulation_collection()
        
        # Create simulation run
        run_id = f"sim_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        simulation_run = SimulationRun(
            run_id=run_id,
            intersection_id=config.intersection_id,
            start_time=datetime.utcnow(),
            status="running",
            config=config
        )
        
        # Insert into database
        result = await collection.insert_one(simulation_run.dict())
        
        # Publish to Redis for simulation controller
        redis_client = get_redis_client()
        await redis_client.publish(
            "simulation:start",
            str(simulation_run.dict())
        )
        
        return {
            "run_id": run_id,
            "message": "Simulation started successfully",
            "status": "running"
        }
        
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{run_id}")
async def get_simulation_run(run_id: str) -> Dict[str, Any]:
    """Get specific simulation run"""
    try:
        collection = get_simulation_collection()
        
        # Get simulation run
        simulation = await collection.find_one({"run_id": run_id})
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation run not found")
        
        return simulation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching simulation run: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{run_id}/stop")
async def stop_simulation(run_id: str) -> Dict[str, Any]:
    """Stop a running simulation"""
    try:
        collection = get_simulation_collection()
        
        # Update simulation status
        result = await collection.update_one(
            {"run_id": run_id},
            {
                "$set": {
                    "status": "stopped",
                    "end_time": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Simulation run not found")
        
        # Publish to Redis for simulation controller
        redis_client = get_redis_client()
        await redis_client.publish(
            "simulation:stop",
            run_id
        )
        
        return {
            "run_id": run_id,
            "message": "Simulation stopped successfully",
            "status": "stopped"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping simulation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{run_id}/results")
async def get_simulation_results(run_id: str) -> Dict[str, Any]:
    """Get simulation results"""
    try:
        collection = get_simulation_collection()
        
        # Get simulation run
        simulation = await collection.find_one({"run_id": run_id})
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation run not found")
        
        if simulation["status"] != "completed":
            raise HTTPException(status_code=400, detail="Simulation not completed")
        
        return simulation.get("results", {})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching simulation results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/current")
async def get_current_simulation_status() -> Dict[str, Any]:
    """Get current simulation status"""
    try:
        collection = get_simulation_collection()
        
        # Get currently running simulation
        running_simulation = await collection.find_one({"status": "running"})
        
        if not running_simulation:
            return {"status": "idle", "message": "No simulation currently running"}
        
        return {
            "status": "running",
            "run_id": running_simulation["run_id"],
            "intersection_id": running_simulation["intersection_id"],
            "start_time": running_simulation["start_time"],
            "duration": (datetime.utcnow() - running_simulation["start_time"]).total_seconds()
        }
        
    except Exception as e:
        logger.error(f"Error fetching current simulation status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
