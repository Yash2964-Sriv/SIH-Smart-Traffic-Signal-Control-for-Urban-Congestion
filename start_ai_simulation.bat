@echo off
echo Complete AI Traffic Simulation
echo ==============================

echo.
echo Starting SUMO with video replication...
start "SUMO GUI" sumo-gui -c video_replication_simulation.sumocfg --remote-port 8813

echo.
echo Waiting for SUMO to initialize...
timeout /t 8 /nobreak > nul

echo.
echo Starting AI Controller...
python simple_working_ai_simulation.py

echo.
echo AI Simulation completed!
echo Check simple_ai_performance.json for results.
pause
