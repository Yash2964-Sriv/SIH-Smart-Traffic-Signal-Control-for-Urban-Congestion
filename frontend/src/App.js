import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import TrafficSimulation from './pages/TrafficSimulation';
import EnhancedTrafficSimulation from './pages/EnhancedTrafficSimulation';
import CameraFeed from './pages/CameraFeed';
import AIModels from './pages/AIModels';
import Metrics from './pages/Metrics';
import Settings from './pages/Settings';
import { useTrafficStore } from './stores/trafficStore';

function App() {
    const { isConnected } = useTrafficStore();

    return (
        <div className="flex h-screen bg-gray-50">
            <Sidebar />
            <main className="flex-1 overflow-hidden">
                <div className="h-full flex flex-col">
                    {/* Header */}
                    <header className="bg-white border-b border-gray-200 px-6 py-4">
                        <div className="flex items-center justify-between">
                            <h1 className="text-2xl font-bold text-gray-900">
                                Smart Traffic Simulator
                            </h1>
                            <div className="flex items-center space-x-4">
                                <div className="flex items-center space-x-2">
                                    <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                    <span className="text-sm text-gray-600">
                                        {isConnected ? 'Connected' : 'Disconnected'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Main Content */}
                    <div className="flex-1 overflow-auto">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                            className="p-6"
                        >
                            <Routes>
                                <Route path="/" element={<Dashboard />} />
                                <Route path="/simulation" element={<TrafficSimulation />} />
                                <Route path="/enhanced-simulation" element={<EnhancedTrafficSimulation />} />
                                <Route path="/camera" element={<CameraFeed />} />
                                <Route path="/ai-models" element={<AIModels />} />
                                <Route path="/metrics" element={<Metrics />} />
                                <Route path="/settings" element={<Settings />} />
                            </Routes>
                        </motion.div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;

