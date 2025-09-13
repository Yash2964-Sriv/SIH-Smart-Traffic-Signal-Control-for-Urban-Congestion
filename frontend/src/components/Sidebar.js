import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  CameraIcon,
  CpuChipIcon,
  ChartBarIcon,
  CogIcon,
  PlayIcon,
  StopIcon,
  VideoCameraIcon
} from '@heroicons/react/24/outline';
import useTrafficStore from '../stores/trafficStore';

const Sidebar = () => {
  const {
    isConnected,
    simulation,
    startSimulation,
    stopSimulation
  } = useTrafficStore();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Traffic Simulation', href: '/simulation', icon: PlayIcon },
    { name: 'Live Video Simulation', href: '/enhanced-simulation', icon: VideoCameraIcon },
    { name: 'Camera Feed', href: '/camera', icon: CameraIcon },
    { name: 'AI Models', href: '/ai', icon: CpuChipIcon },
    { name: 'Metrics', href: '/metrics', icon: ChartBarIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  return (
    <div className="flex flex-col w-64 bg-gray-900 text-white">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 bg-gray-800">
        <h1 className="text-xl font-bold">Smart Traffic</h1>
      </div>

      {/* Connection Status */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
          <span className="text-sm">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                ? 'bg-gray-700 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Simulation Controls */}
      <div className="px-4 py-4 border-t border-gray-700">
        <button
          onClick={simulation.isRunning ? stopSimulation : startSimulation}
          className={`w-full flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${simulation.isRunning
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
        >
          {simulation.isRunning ? (
            <>
              <StopIcon className="w-4 h-4 mr-2" />
              Stop Simulation
            </>
          ) : (
            <>
              <PlayIcon className="w-4 h-4 mr-2" />
              Start Simulation
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
