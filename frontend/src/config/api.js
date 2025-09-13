// API Configuration
const API_CONFIG = {
    // Backend API base URL
    BASE_URL: 'http://localhost:5000',

    // API endpoints
    ENDPOINTS: {
        UPLOAD_VIDEO: '/api/upload-video',
        START_LIVE_SIMULATION: '/api/start-live-simulation',
        LIVE_METRICS: '/api/live-metrics',
        START_SIMULATION: '/api/start',
        STOP_SIMULATION: '/api/stop',
        METRICS: '/api/metrics',
        AI_DECISIONS: '/api/ai/decisions'
    }
};

// Helper function to get full API URL
export const getApiUrl = (endpoint) => {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Export individual endpoint URLs
export const API_URLS = {
    UPLOAD_VIDEO: getApiUrl(API_CONFIG.ENDPOINTS.UPLOAD_VIDEO),
    START_LIVE_SIMULATION: getApiUrl(API_CONFIG.ENDPOINTS.START_LIVE_SIMULATION),
    LIVE_METRICS: getApiUrl(API_CONFIG.ENDPOINTS.LIVE_METRICS),
    START_SIMULATION: getApiUrl(API_CONFIG.ENDPOINTS.START_SIMULATION),
    STOP_SIMULATION: getApiUrl(API_CONFIG.ENDPOINTS.STOP_SIMULATION),
    METRICS: getApiUrl(API_CONFIG.ENDPOINTS.METRICS),
    AI_DECISIONS: getApiUrl(API_CONFIG.ENDPOINTS.AI_DECISIONS)
};

export default API_CONFIG;


