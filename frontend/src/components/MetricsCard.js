import React from 'react';
import { motion } from 'framer-motion';

function MetricsCard({ title, value, change, changeType, icon }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="card"
        >
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-600">{title}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
                    <div className="flex items-center mt-2">
                        <span
                            className={`text-sm font-medium ${changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                                }`}
                        >
                            {change}
                        </span>
                        <span className="text-sm text-gray-500 ml-1">from last hour</span>
                    </div>
                </div>
                <div className="text-3xl">{icon}</div>
            </div>
        </motion.div>
    );
}

export default MetricsCard;

