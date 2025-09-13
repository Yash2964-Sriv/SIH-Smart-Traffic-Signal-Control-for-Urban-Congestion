import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { useTrafficStore } from '../stores/trafficStore';
import { API_URLS } from '../config/api';

function EnhancedTrafficSimulation() {
    const {
        simulation,
        trafficLights,
        startSimulation,
        stopSimulation,
        isConnected
    } = useTrafficStore();

    // New state for video upload and live simulation
    const [uploadedVideo, setUploadedVideo] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [liveSimulation, setLiveSimulation] = useState({
        isRunning: false,
        videoPath: null,
        metrics: null,
        aiPerformance: null,
        comparisonData: null
    });
    const [isUploading, setIsUploading] = useState(false);
    const [isStartingSimulation, setIsStartingSimulation] = useState(false);
    const fileInputRef = useRef(null);
    const metricsIntervalRef = useRef(null);

    useEffect(() => {
        // Auto-connect when component mounts
        if (!isConnected) {
            // Auto-connection logic if needed
        }
    }, [isConnected]);

    // Cleanup interval on unmount
    useEffect(() => {
        return () => {
            if (metricsIntervalRef.current) {
                clearInterval(metricsIntervalRef.current);
            }
        };
    }, []);

    const handleVideoUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsUploading(true);
        setUploadStatus('Uploading video...');

        const formData = new FormData();
        formData.append('video', file);

        try {
            const response = await fetch(API_URLS.UPLOAD_VIDEO, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                setUploadedVideo({
                    file: file,
                    filename: result.filename,
                    filepath: result.filepath
                });
                setUploadStatus('Video uploaded successfully!');
            } else {
                setUploadStatus(`Upload failed: ${result.message}`);
            }
        } catch (error) {
            setUploadStatus(`Upload error: ${error.message}`);
        } finally {
            setIsUploading(false);
        }
    };

    const startLiveSimulation = async () => {
        if (!uploadedVideo) {
            setUploadStatus('Please upload a video first');
            return;
        }

        setIsStartingSimulation(true);
        setUploadStatus('Starting live simulation...');

        try {
            const response = await fetch(API_URLS.START_LIVE_SIMULATION, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    video_path: uploadedVideo.filepath
                })
            });

            const result = await response.json();

            if (result.success) {
                setLiveSimulation(prev => ({
                    ...prev,
                    isRunning: true,
                    videoPath: result.video_path
                }));
                setUploadStatus('Live simulation started! SUMO GUI will open shortly...');

                // Start polling for metrics
                startMetricsPolling();
            } else {
                setUploadStatus(`Simulation failed: ${result.message}`);
            }
        } catch (error) {
            setUploadStatus(`Simulation error: ${error.message}`);
        } finally {
            setIsStartingSimulation(false);
        }
    };

    const startMetricsPolling = () => {
        metricsIntervalRef.current = setInterval(async () => {
            try {
                const response = await fetch(API_URLS.LIVE_METRICS);
                const metrics = await response.json();

                if (metrics.simulation_running) {
                    setLiveSimulation(prev => ({
                        ...prev,
                        metrics: metrics.metrics,
                        aiPerformance: metrics.ai_performance,
                        comparisonData: metrics.comparison_data
                    }));
                }
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }, 2000); // Poll every 2 seconds
    };

    const stopLiveSimulation = () => {
        setLiveSimulation({
            isRunning: false,
            videoPath: null,
            metrics: null,
            aiPerformance: null,
            comparisonData: null
        });

        if (metricsIntervalRef.current) {
            clearInterval(metricsIntervalRef.current);
            metricsIntervalRef.current = null;
        }

        setUploadStatus('Live simulation stopped');
    };

    const resetUpload = () => {
        setUploadedVideo(null);
        setUploadStatus('');
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Enhanced Traffic Simulation</h1>
                <p className="text-gray-600 mt-1">
                    Upload real traffic video and run AI-controlled SUMO simulation with live comparison
                </p>
            </div>

            {/* Video Upload Section */}
            <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">📹 Upload Real Traffic Video</h2>

                <div className="space-y-4">
                    <div className="flex items-center space-x-4">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="video/*"
                            onChange={handleVideoUpload}
                            className="hidden"
                            id="video-upload"
                        />
                        <label
                            htmlFor="video-upload"
                            className="btn-primary cursor-pointer"
                        >
                            {isUploading ? 'Uploading...' : 'Choose Video File'}
                        </label>

                        {uploadedVideo && (
                            <button
                                onClick={resetUpload}
                                className="btn-secondary"
                            >
                                Reset
                            </button>
                        )}
                    </div>

                    {uploadedVideo && (
                        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-green-800 font-medium">
                                ✅ Video Ready: {uploadedVideo.filename}
                            </p>
                            <p className="text-green-600 text-sm mt-1">
                                File size: {(uploadedVideo.file.size / (1024 * 1024)).toFixed(2)} MB
                            </p>
                        </div>
                    )}

                    {uploadStatus && (
                        <div className={`p-3 rounded-lg ${uploadStatus.includes('success') || uploadStatus.includes('started')
                            ? 'bg-green-50 text-green-800'
                            : 'bg-red-50 text-red-800'
                            }`}>
                            {uploadStatus}
                        </div>
                    )}
                </div>
            </div>

            {/* Live Simulation Controls */}
            <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">🚦 Live SUMO Simulation</h2>

                <div className="flex items-center space-x-4 mb-4">
                    <button
                        onClick={startLiveSimulation}
                        disabled={!uploadedVideo || isStartingSimulation || liveSimulation.isRunning}
                        className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isStartingSimulation ? 'Starting...' : 'Start Live Simulation'}
                    </button>

                    <button
                        onClick={stopLiveSimulation}
                        disabled={!liveSimulation.isRunning}
                        className="btn-danger disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Stop Simulation
                    </button>
                </div>

                {liveSimulation.isRunning && (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-blue-800 font-medium">
                            🎬 Live simulation running with video: {uploadedVideo?.filename}
                        </p>
                        <p className="text-blue-600 text-sm mt-1">
                            SUMO GUI should be open. AI is controlling traffic signals in real-time.
                        </p>
                    </div>
                )}
            </div>

            {/* Live Metrics Display */}
            {liveSimulation.isRunning && liveSimulation.metrics && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* AI Performance Metrics */}
                    {liveSimulation.aiPerformance && (
                        <div className="card">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI Performance</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Overall Performance:</span>
                                    <span className="font-semibold text-green-600">
                                        {liveSimulation.aiPerformance.overall_ai_performance?.toFixed(1) || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Accuracy Score:</span>
                                    <span className="font-semibold text-blue-600">
                                        {liveSimulation.aiPerformance.accuracy_score?.toFixed(1) || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Efficiency Score:</span>
                                    <span className="font-semibold text-purple-600">
                                        {liveSimulation.aiPerformance.efficiency_score?.toFixed(1) || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Real-time Processing:</span>
                                    <span className="font-semibold text-orange-600">
                                        {(liveSimulation.aiPerformance.real_time_processing_capability * 100)?.toFixed(1) || 0}%
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Comparison Data */}
                    {liveSimulation.comparisonData && (
                        <div className="card">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 AI vs Real Traffic</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Pattern Accuracy:</span>
                                    <span className="font-semibold text-green-600">
                                        {liveSimulation.comparisonData.accuracy_metrics?.overall_pattern_accuracy?.toFixed(1) || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Efficiency Improvement:</span>
                                    <span className="font-semibold text-blue-600">
                                        +{liveSimulation.comparisonData.efficiency_improvements?.overall_efficiency?.toFixed(1) || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Time Saved:</span>
                                    <span className="font-semibold text-purple-600">
                                        {liveSimulation.comparisonData.efficiency_improvements?.time_saved?.toFixed(1) || 0}s
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Traffic Reduction:</span>
                                    <span className="font-semibold text-orange-600">
                                        -{liveSimulation.comparisonData.efficiency_improvements?.traffic_reduction?.toFixed(1) || 0}%
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Live Simulation Status */}
                    <div className="card">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Live Status</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Status:</span>
                                <span className="font-semibold text-green-600">Running</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Video:</span>
                                <span className="font-semibold text-blue-600">
                                    {uploadedVideo?.filename?.substring(0, 20)}...
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">AI Control:</span>
                                <span className="font-semibold text-green-600">Active</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">SUMO GUI:</span>
                                <span className="font-semibold text-green-600">Open</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Instructions */}
            <div className="card bg-gray-50">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 How to Use</h3>
                <div className="space-y-2 text-gray-700">
                    <p>1. <strong>Upload Video:</strong> Choose a real traffic video file (MP4, AVI, MOV, WEBM, MKV)</p>
                    <p>2. <strong>Start Simulation:</strong> Click "Start Live Simulation" to begin AI analysis</p>
                    <p>3. <strong>Watch SUMO:</strong> SUMO GUI will open showing the replicated traffic</p>
                    <p>4. <strong>AI Control:</strong> AI will automatically control traffic signals for better efficiency</p>
                    <p>5. <strong>Live Metrics:</strong> Monitor real-time comparison between AI and real traffic</p>
                </div>
            </div>

            {/* Original Simulation Controls (Fallback) */}
            <div className="card">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-semibold text-gray-900">Basic Simulation Controls</h2>
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={startSimulation}
                            disabled={simulation.isRunning}
                            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Start Basic Simulation
                        </button>
                        <button
                            onClick={stopSimulation}
                            disabled={!simulation.isRunning}
                            className="btn-danger disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Stop Simulation
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default EnhancedTrafficSimulation;
