import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTrafficStore } from '../stores/trafficStore';
import TrafficLightDisplay from '../components/TrafficLightDisplay';
import MetricsCard from '../components/MetricsCard';
import TrafficFlowChart from '../components/TrafficFlowChart';

function Dashboard() {
    const {
        connect,
        isConnected,
        trafficData,
        trafficLights,
        simulation,
        aiModel,
        metrics
    } = useTrafficStore();

    useEffect(() => {
        if (!isConnected) {
            connect();
        }
    }, [connect, isConnected]);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-600 mt-1">
                        Real-time traffic simulation and AI control overview
                    </p>
                </div>
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span className="text-sm text-gray-600">
                            {isConnected ? 'Connected' : 'Disconnected'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricsCard
                    title="Total Vehicles"
                    value={metrics?.totalVehicles || 0}
                    change="+12%"
                    changeType="positive"
                    icon="🚗"
                />
                <MetricsCard
                    title="Average Wait Time"
                    value={`${(metrics?.averageWaitTime || 0).toFixed(1)}s`}
                    change="-8%"
                    changeType="negative"
                    icon="⏱️"
                />
                <MetricsCard
                    title="Queue Length"
                    value={metrics?.queueLength || 0}
                    change="+15%"
                    changeType="positive"
                    icon="📈"
                />
                <MetricsCard
                    title="Throughput"
                    value={`${(metrics?.throughput || 0).toFixed(1)}`}
                    change="+5%"
                    changeType="positive"
                    icon="🤖"
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Traffic Light Status */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                    className="lg:col-span-1"
                >
                    <div className="card">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            Traffic Light Status
                        </h2>
                        <TrafficLightDisplay lights={trafficLights} />
                        <div className="mt-4 space-y-2">
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-600">Current Phase:</span>
                                <span className="font-medium">{simulation?.currentPhase || 'N/A'}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-600">Phase Time:</span>
                                <span className="font-medium">{simulation?.phaseTime || 0}s</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-600">AI Active:</span>
                                <span className={`font-medium ${aiModel?.isActive ? 'text-green-600' : 'text-red-600'}`}>
                                    {aiModel?.isActive ? 'Yes' : 'No'}
                                </span>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Traffic Flow Chart */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="lg:col-span-2"
                >
                    <div className="card">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            Traffic Flow Overview
                        </h2>
                        <TrafficFlowChart data={trafficData} />
                    </div>
                </motion.div>
            </div>

            {/* Lane Details */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
            >
                <div className="card">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">
                        Lane Performance
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {Object.entries(trafficData).map(([direction, data]) => (
                            <div key={direction} className="bg-gray-50 rounded-lg p-4">
                                <h3 className="font-medium text-gray-900 capitalize mb-2">
                                    {direction} Lane
                                </h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Queue:</span>
                                        <span className="font-medium">{data.queue}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Flow:</span>
                                        <span className="font-medium">{data.flow} vph</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Wait:</span>
                                        <span className="font-medium">{data.waitTime}s</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </motion.div>
        </div>
    );
}

export default Dashboard;

