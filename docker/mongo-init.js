// MongoDB initialization script
db = db.getSiblingDB('traffic_simulator');

// Create collections
db.createCollection('traffic_data');
db.createCollection('simulation_runs');
db.createCollection('ai_models');
db.createCollection('camera_feeds');
db.createCollection('performance_metrics');
db.createCollection('configurations');

// Create indexes for better performance
db.traffic_data.createIndex({ "timestamp": 1 });
db.traffic_data.createIndex({ "intersection_id": 1, "timestamp": 1 });
db.simulation_runs.createIndex({ "start_time": 1 });
db.simulation_runs.createIndex({ "status": 1 });
db.ai_models.createIndex({ "model_name": 1 });
db.ai_models.createIndex({ "created_at": 1 });
db.camera_feeds.createIndex({ "camera_id": 1, "timestamp": 1 });
db.performance_metrics.createIndex({ "run_id": 1, "timestamp": 1 });

// Insert default configuration
db.configurations.insertOne({
    "config_id": "default",
    "intersection_config": {
        "num_lanes": 4,
        "signal_phases": [
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
        ],
        "yellow_duration": 3,
        "red_duration": 2
    },
    "ai_config": {
        "model_type": "PPO",
        "learning_rate": 0.0003,
        "batch_size": 64,
        "update_frequency": 1000
    },
    "camera_config": {
        "fps": 30,
        "resolution": "1920x1080",
        "detection_confidence": 0.5
    },
    "created_at": new Date(),
    "updated_at": new Date()
});

// Insert sample traffic data structure
db.traffic_data.insertOne({
    "intersection_id": "sample_intersection",
    "timestamp": new Date(),
    "lane_data": {
        "north_1": {
            "queue_length": 5,
            "throughput": 12,
            "wait_time": 45
        },
        "north_2": {
            "queue_length": 3,
            "throughput": 8,
            "wait_time": 30
        },
        "south_1": {
            "queue_length": 7,
            "throughput": 15,
            "wait_time": 60
        },
        "south_2": {
            "queue_length": 4,
            "throughput": 10,
            "wait_time": 35
        },
        "east_1": {
            "queue_length": 2,
            "throughput": 6,
            "wait_time": 20
        },
        "east_2": {
            "queue_length": 1,
            "throughput": 4,
            "wait_time": 15
        },
        "west_1": {
            "queue_length": 6,
            "throughput": 14,
            "wait_time": 50
        },
        "west_2": {
            "queue_length": 3,
            "throughput": 9,
            "wait_time": 25
        }
    },
    "signal_state": {
        "current_phase": "NS",
        "phase_duration": 25,
        "next_phase": "EW"
    },
    "ai_decision": {
        "action": "extend_green",
        "confidence": 0.85,
        "reasoning": "High queue length on north-south lanes"
    }
});

print("MongoDB initialization completed successfully!");
