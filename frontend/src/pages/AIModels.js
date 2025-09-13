import React from 'react';
import { useTrafficStore } from '../stores/trafficStore';

function AIModels() {
    const { aiModel, activateAI, deactivateAI } = useTrafficStore();

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">AI Models</h1>
                <p className="text-gray-600 mt-1">
                    Manage and monitor AI models for traffic control
                </p>
            </div>

            <div className="card">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-semibold text-gray-900">AI Control</h2>
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={activateAI}
                            disabled={aiModel.isActive}
                            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Activate AI
                        </button>
                        <button
                            onClick={deactivateAI}
                            disabled={!aiModel.isActive}
                            className="btn-danger disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Deactivate AI
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-gray-50 rounded-lg p-4">
                        <h3 className="font-medium text-gray-900 mb-3">AI Status</h3>
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Status:</span>
                                <span className={`font-medium ${aiModel.isActive ? 'text-green-600' : 'text-red-600'}`}>
                                    {aiModel.isActive ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Model Type:</span>
                                <span className="font-medium">{aiModel.modelType}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Confidence:</span>
                                <span className="font-medium">{(aiModel.confidence * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <h3 className="font-medium text-gray-900 mb-3">Last Decision</h3>
                        <div className="space-y-2">
                            {aiModel.lastDecision ? (
                                <div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Phase:</span>
                                        <span className="font-medium">{aiModel.lastDecision.phase}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Duration:</span>
                                        <span className="font-medium">{aiModel.lastDecision.duration}s</span>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-gray-500">No decisions made yet</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AIModels;

