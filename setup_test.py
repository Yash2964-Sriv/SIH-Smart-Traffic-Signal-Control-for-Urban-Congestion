#!/usr/bin/env python3
"""
Setup test script for Smart Traffic Simulator
This script tests the basic setup and configuration
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_directory_structure():
    """Test if all required directories exist"""
    logger.info("Testing directory structure...")
    
    required_dirs = [
        "backend",
        "frontend", 
        "simulation",
        "omniverse",
        "ai_controller",
        "camera_integration",
        "docker",
        "docs",
        "data",
        "config",
        "backend/routers"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        logger.error(f"Missing directories: {missing_dirs}")
        return False
    
    logger.info("✓ All required directories exist")
    return True


def test_config_files():
    """Test if configuration files exist"""
    logger.info("Testing configuration files...")
    
    required_files = [
        "requirements.txt",
        "docker-compose.yml",
        "config/settings.py",
        "config/env_template.txt",
        "docker/backend.Dockerfile",
        "docker/frontend.Dockerfile",
        "docker/node-backend.Dockerfile",
        "docker/sumo.Dockerfile",
        "docker/ai-controller.Dockerfile",
        "docker/camera-integration.Dockerfile",
        "docker/nginx.conf",
        "docker/mongo-init.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing files: {missing_files}")
        return False
    
    logger.info("✓ All configuration files exist")
    return True


def test_backend_files():
    """Test if backend files exist"""
    logger.info("Testing backend files...")
    
    required_files = [
        "backend/main.py",
        "backend/database.py",
        "backend/routers/__init__.py",
        "backend/routers/traffic.py",
        "backend/routers/simulation.py",
        "backend/routers/ai.py",
        "backend/routers/metrics.py",
        "backend/routers/camera.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing backend files: {missing_files}")
        return False
    
    logger.info("✓ All backend files exist")
    return True


def test_python_imports():
    """Test if Python modules can be imported"""
    logger.info("Testing Python imports...")
    
    try:
        # Test config import
        from config.settings import settings
        logger.info("✓ Config settings imported successfully")
        
        # Test backend imports
        from backend.database import get_mongodb_database, get_redis_client
        logger.info("✓ Backend database module imported successfully")
        
        # Test router imports
        from backend.routers import traffic, simulation, ai, metrics, camera
        logger.info("✓ All routers imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during import test: {e}")
        return False


def test_docker_config():
    """Test Docker configuration"""
    logger.info("Testing Docker configuration...")
    
    try:
        # Check if docker-compose.yml is valid
        import yaml
        with open("docker-compose.yml", "r") as f:
            yaml.safe_load(f)
        logger.info("✓ Docker Compose configuration is valid")
        
        return True
        
    except Exception as e:
        logger.error(f"Docker configuration error: {e}")
        return False


def test_environment_setup():
    """Test environment setup"""
    logger.info("Testing environment setup...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        logger.error(f"Python 3.9+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    logger.info(f"✓ Python version {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if required directories are created
    data_dirs = ["data", "data/models", "data/traffic", "logs"]
    for dir_path in data_dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"✓ Created directory: {dir_path}")
    
    return True


async def test_async_components():
    """Test async components"""
    logger.info("Testing async components...")
    
    try:
        # Test if asyncio works
        await asyncio.sleep(0.1)
        logger.info("✓ Async functionality works")
        
        return True
        
    except Exception as e:
        logger.error(f"Async test error: {e}")
        return False


def main():
    """Main test function"""
    logger.info("Starting Smart Traffic Simulator setup test...")
    logger.info("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Configuration Files", test_config_files),
        ("Backend Files", test_backend_files),
        ("Python Imports", test_python_imports),
        ("Docker Configuration", test_docker_config),
        ("Environment Setup", test_environment_setup),
        ("Async Components", lambda: asyncio.run(test_async_components()))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} test...")
        try:
            if test_func():
                logger.info(f"✓ {test_name} test PASSED")
                passed += 1
            else:
                logger.error(f"✗ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} test FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Setup is complete and ready.")
        logger.info("\nNext steps:")
        logger.info("1. Copy config/env_template.txt to .env and configure your settings")
        logger.info("2. Install Python dependencies: pip install -r requirements.txt")
        logger.info("3. Start the services: docker-compose up -d")
        logger.info("4. Access the application at http://localhost")
        return True
    else:
        logger.error("❌ Some tests failed. Please fix the issues before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
