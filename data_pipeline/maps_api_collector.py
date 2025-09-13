"""
Maps API Data Collector
Handles data collection from various mapping APIs (Google Maps, HERE, etc.)
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class MapsAPICollector:
    def __init__(self, api_key: str, provider: str = "google"):
        """
        Initialize Maps API collector
        
        Args:
            api_key: API key for the mapping service
            provider: API provider ("google", "here", "mapbox")
        """
        self.api_key = api_key
        self.provider = provider
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SmartTrafficSimulator/1.0'
        })
        
        # API endpoints
        self.endpoints = {
            'google': {
                'traffic': 'https://maps.googleapis.com/maps/api/distancematrix/json',
                'places': 'https://maps.googleapis.com/maps/api/place/nearbysearch/json',
                'directions': 'https://maps.googleapis.com/maps/api/directions/json'
            },
            'here': {
                'traffic': 'https://traffic.ls.hereapi.com/traffic/6.3/flow.json',
                'places': 'https://places.ls.hereapi.com/places/v1/discover/search',
                'directions': 'https://route.ls.hereapi.com/routing/7.2/calculateroute.json'
            }
        }
    
    def get_traffic_data(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
        """
        Get traffic data between two points
        
        Args:
            origin: (lat, lon) of origin
            destination: (lat, lon) of destination
            
        Returns:
            Dictionary containing traffic data
        """
        if self.provider == "google":
            return self._get_google_traffic_data(origin, destination)
        elif self.provider == "here":
            return self._get_here_traffic_data(origin, destination)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return {}
    
    def _get_google_traffic_data(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
        """Get traffic data from Google Maps API"""
        try:
            params = {
                'origins': f"{origin[0]},{origin[1]}",
                'destinations': f"{destination[0]},{destination[1]}",
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'key': self.api_key
            }
            
            response = self.session.get(
                self.endpoints['google']['traffic'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                element = data['rows'][0]['elements'][0]
                return {
                    'duration': element['duration']['value'],
                    'duration_in_traffic': element.get('duration_in_traffic', {}).get('value', 0),
                    'distance': element['distance']['value'],
                    'status': element['status'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Google Maps API error: {data.get('error_message', 'Unknown error')}")
                return {}
                
        except Exception as e:
            logger.error(f"Google Maps API request error: {e}")
            return {}
    
    def _get_here_traffic_data(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
        """Get traffic data from HERE API"""
        try:
            params = {
                'waypoint0': f"geo!{origin[0]},{origin[1]}",
                'waypoint1': f"geo!{destination[0]},{destination[1]}",
                'mode': 'fastest;car;traffic:enabled',
                'apikey': self.api_key
            }
            
            response = self.session.get(
                self.endpoints['here']['directions'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'response' in data and data['response']['route']:
                route = data['response']['route'][0]
                summary = route['summary']
                return {
                    'duration': summary['travelTime'],
                    'distance': summary['distance'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("HERE API error: No route found")
                return {}
                
        except Exception as e:
            logger.error(f"HERE API request error: {e}")
            return {}
    
    def get_nearby_places(self, location: Tuple[float, float], radius: int = 1000, place_type: str = "restaurant") -> List[Dict]:
        """
        Get nearby places that might affect traffic
        
        Args:
            location: (lat, lon) of center point
            radius: Search radius in meters
            place_type: Type of place to search for
            
        Returns:
            List of nearby places
        """
        if self.provider == "google":
            return self._get_google_nearby_places(location, radius, place_type)
        elif self.provider == "here":
            return self._get_here_nearby_places(location, radius, place_type)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return []
    
    def _get_google_nearby_places(self, location: Tuple[float, float], radius: int, place_type: str) -> List[Dict]:
        """Get nearby places from Google Places API"""
        try:
            params = {
                'location': f"{location[0]},{location[1]}",
                'radius': radius,
                'type': place_type,
                'key': self.api_key
            }
            
            response = self.session.get(
                self.endpoints['google']['places'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                places = []
                for place in data['results']:
                    places.append({
                        'name': place['name'],
                        'place_id': place['place_id'],
                        'location': place['geometry']['location'],
                        'rating': place.get('rating', 0),
                        'types': place.get('types', []),
                        'vicinity': place.get('vicinity', '')
                    })
                return places
            else:
                logger.error(f"Google Places API error: {data.get('error_message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Google Places API request error: {e}")
            return []
    
    def _get_here_nearby_places(self, location: Tuple[float, float], radius: int, place_type: str) -> List[Dict]:
        """Get nearby places from HERE Places API"""
        try:
            params = {
                'at': f"{location[0]},{location[1]}",
                'q': place_type,
                'apikey': self.api_key
            }
            
            response = self.session.get(
                self.endpoints['here']['places'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data:
                places = []
                for item in data['results']['items']:
                    places.append({
                        'name': item['title'],
                        'place_id': item['id'],
                        'location': item['position'],
                        'distance': item.get('distance', 0),
                        'categories': item.get('categories', [])
                    })
                return places
            else:
                logger.error("HERE Places API error: No results found")
                return []
                
        except Exception as e:
            logger.error(f"HERE Places API request error: {e}")
            return []
    
    def get_historical_traffic_data(self, origin: Tuple[float, float], destination: Tuple[float, float], 
                                  days_back: int = 7) -> List[Dict]:
        """
        Get historical traffic data for analysis
        
        Args:
            origin: (lat, lon) of origin
            destination: (lat, lon) of destination
            days_back: Number of days to look back
            
        Returns:
            List of historical traffic data points
        """
        historical_data = []
        
        for i in range(days_back):
            # Calculate timestamp for each day
            target_time = datetime.now() - timedelta(days=i)
            target_timestamp = int(target_time.timestamp())
            
            # Get traffic data for that time
            traffic_data = self.get_traffic_data(origin, destination)
            if traffic_data:
                traffic_data['historical_date'] = target_time.isoformat()
                traffic_data['historical_timestamp'] = target_timestamp
                historical_data.append(traffic_data)
            
            # Rate limiting
            time.sleep(0.1)
        
        return historical_data
    
    def get_route_alternatives(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> List[Dict]:
        """
        Get alternative routes between two points
        
        Args:
            origin: (lat, lon) of origin
            destination: (lat, lon) of destination
            
        Returns:
            List of alternative routes
        """
        if self.provider == "google":
            return self._get_google_route_alternatives(origin, destination)
        elif self.provider == "here":
            return self._get_here_route_alternatives(origin, destination)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return []
    
    def _get_google_route_alternatives(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> List[Dict]:
        """Get alternative routes from Google Directions API"""
        try:
            params = {
                'origin': f"{origin[0]},{origin[1]}",
                'destination': f"{destination[0]},{destination[1]}",
                'alternatives': 'true',
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'key': self.api_key
            }
            
            response = self.session.get(
                self.endpoints['google']['directions'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                routes = []
                for route in data['routes']:
                    leg = route['legs'][0]
                    routes.append({
                        'duration': leg['duration']['value'],
                        'duration_in_traffic': leg.get('duration_in_traffic', {}).get('value', 0),
                        'distance': leg['distance']['value'],
                        'summary': route['summary'],
                        'steps': [step['html_instructions'] for step in leg['steps']]
                    })
                return routes
            else:
                logger.error(f"Google Directions API error: {data.get('error_message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Google Directions API request error: {e}")
            return []
    
    def _get_here_route_alternatives(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> List[Dict]:
        """Get alternative routes from HERE Directions API"""
        try:
            params = {
                'waypoint0': f"geo!{origin[0]},{origin[1]}",
                'waypoint1': f"geo!{destination[0]},{destination[1]}",
                'mode': 'fastest;car;traffic:enabled',
                'alternatives': '3',
                'apikey': self.api_key
            }
            
            response = self.session.get(
                self.endpoints['here']['directions'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'response' in data and data['response']['route']:
                routes = []
                for route in data['response']['route']:
                    summary = route['summary']
                    routes.append({
                        'duration': summary['travelTime'],
                        'distance': summary['distance'],
                        'summary': route.get('summary', {}),
                        'waypoints': len(route['waypoint'])
                    })
                return routes
            else:
                logger.error("HERE Directions API error: No routes found")
                return []
                
        except Exception as e:
            logger.error(f"HERE Directions API request error: {e}")
            return []
    
    def save_traffic_data(self, traffic_data: Dict, filename: str) -> bool:
        """
        Save traffic data to file
        
        Args:
            traffic_data: Traffic data to save
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(traffic_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Traffic data saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Traffic data save error: {e}")
            return False
