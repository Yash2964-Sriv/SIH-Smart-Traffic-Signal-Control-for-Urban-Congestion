import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function TrafficFlowChart({ data }) {
    const chartData = Object.entries(data).map(([direction, metrics]) => ({
        direction: direction.charAt(0).toUpperCase() + direction.slice(1),
        queue: metrics.queue,
        flow: metrics.flow,
        waitTime: metrics.waitTime,
    }));

    return (
        <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="direction" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="queue" fill="#3b82f6" name="Queue Length" />
                    <Bar dataKey="flow" fill="#10b981" name="Flow Rate" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

export default TrafficFlowChart;

