import React from 'react';
import { motion } from 'framer-motion';

function TrafficLightDisplay({ lights }) {
    const directions = ['north', 'south', 'east', 'west'];

    return (
        <div className="grid grid-cols-2 gap-4">
            {directions.map((direction) => (
                <div key={direction} className="text-center">
                    <div className="text-sm font-medium text-gray-700 capitalize mb-2">
                        {direction}
                    </div>
                    <div className="flex flex-col items-center space-y-1">
                        <motion.div
                            className={`traffic-light ${lights[direction] === 'red' ? 'red' : 'off'}`}
                            animate={{
                                scale: lights[direction] === 'red' ? [1, 1.1, 1] : 1,
                            }}
                            transition={{
                                duration: 2,
                                repeat: lights[direction] === 'red' ? Infinity : 0,
                            }}
                        />
                        <motion.div
                            className={`traffic-light ${lights[direction] === 'yellow' ? 'yellow' : 'off'}`}
                            animate={{
                                scale: lights[direction] === 'yellow' ? [1, 1.1, 1] : 1,
                            }}
                            transition={{
                                duration: 1,
                                repeat: lights[direction] === 'yellow' ? Infinity : 0,
                            }}
                        />
                        <motion.div
                            className={`traffic-light ${lights[direction] === 'green' ? 'green' : 'off'}`}
                            animate={{
                                scale: lights[direction] === 'green' ? [1, 1.1, 1] : 1,
                            }}
                            transition={{
                                duration: 2,
                                repeat: lights[direction] === 'green' ? Infinity : 0,
                            }}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
}

export default TrafficLightDisplay;

