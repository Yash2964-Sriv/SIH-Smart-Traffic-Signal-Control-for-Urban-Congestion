import React from 'react';

function CameraFeed() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Camera Feed</h1>
                <p className="text-gray-600 mt-1">
                    Live camera feed and vehicle detection
                </p>
            </div>

            <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Live Camera Feed</h2>
                <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
                    <p className="text-gray-500">Camera feed will be integrated here</p>
                </div>
            </div>
        </div>
    );
}

export default CameraFeed;

