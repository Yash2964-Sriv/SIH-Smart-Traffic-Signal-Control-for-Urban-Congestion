"""
OpenStreetMap Data Collector
Handles OSM data extraction and network generation for SUMO
"""

import requests
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class OSMCollector:
    def __init__(self, overpass_url: str = "https://overpass-api.de/api/interpreter"):
        """
        Initialize OSM collector
        
        Args:
            overpass_url: Overpass API endpoint
        """
        self.overpass_url = overpass_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SmartTrafficSimulator/1.0'
        })
    
    def query_intersection_data(self, lat: float, lon: float, radius: float = 100) -> Dict:
        """
        Query OSM data for intersection area
        
        Args:
            lat: Latitude of intersection center
            lon: Longitude of intersection center
            radius: Search radius in meters
            
        Returns:
            Dictionary containing OSM data
        """
        # Overpass QL query for intersection data
        query = f"""
        [out:json][timeout:25];
        (
          way["highway"~"^(primary|secondary|tertiary|residential|trunk|motorway)$"](around:{radius},{lat},{lon});
          node["highway"~"^(traffic_signals|stop|give_way)$"](around:{radius},{lat},{lon});
          relation["type"="route"]["route"~"^(bus|tram)$"](around:{radius},{lat},{lon});
        );
        out geom;
        """
        
        try:
            response = self.session.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OSM query error: {e}")
            return {}
    
    def extract_road_network(self, osm_data: Dict) -> Dict:
        """
        Extract road network information from OSM data
        
        Args:
            osm_data: Raw OSM data from Overpass API
            
        Returns:
            Dictionary containing road network data
        """
        roads = []
        nodes = {}
        traffic_signals = []
        
        # Process nodes
        for element in osm_data.get('elements', []):
            if element['type'] == 'node':
                node_id = element['id']
                nodes[node_id] = {
                    'id': node_id,
                    'lat': element['lat'],
                    'lon': element['lon'],
                    'tags': element.get('tags', {})
                }
                
                # Check for traffic signals
                if element.get('tags', {}).get('highway') in ['traffic_signals', 'stop', 'give_way']:
                    traffic_signals.append({
                        'id': node_id,
                        'lat': element['lat'],
                        'lon': element['lon'],
                        'type': element['tags']['highway']
                    })
        
        # Process ways (roads)
        for element in osm_data.get('elements', []):
            if element['type'] == 'way':
                way_id = element['id']
                tags = element.get('tags', {})
                
                # Extract road properties
                road = {
                    'id': way_id,
                    'nodes': element.get('nodes', []),
                    'geometry': element.get('geometry', []),
                    'name': tags.get('name', ''),
                    'highway_type': tags.get('highway', ''),
                    'lanes': self._extract_lanes(tags),
                    'maxspeed': self._extract_speed(tags),
                    'oneway': tags.get('oneway', 'no') == 'yes',
                    'surface': tags.get('surface', ''),
                    'width': self._extract_width(tags)
                }
                
                roads.append(road)
        
        return {
            'roads': roads,
            'nodes': nodes,
            'traffic_signals': traffic_signals,
            'metadata': {
                'total_roads': len(roads),
                'total_nodes': len(nodes),
                'traffic_signals': len(traffic_signals),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _extract_lanes(self, tags: Dict) -> int:
        """Extract number of lanes from OSM tags"""
        lanes = tags.get('lanes', '')
        if isinstance(lanes, str) and lanes.isdigit():
            return int(lanes)
        elif isinstance(lanes, (int, float)):
            return int(lanes)
        else:
            # Estimate based on highway type
            highway_type = tags.get('highway', '')
            if highway_type in ['motorway', 'trunk']:
                return 4
            elif highway_type in ['primary', 'secondary']:
                return 2
            else:
                return 1
    
    def _extract_speed(self, tags: Dict) -> float:
        """Extract speed limit from OSM tags"""
        maxspeed = tags.get('maxspeed', '')
        if isinstance(maxspeed, str):
            # Handle different speed formats
            if maxspeed.endswith(' mph'):
                return float(maxspeed[:-4]) * 1.60934  # Convert to km/h
            elif maxspeed.endswith(' km/h'):
                return float(maxspeed[:-5])
            elif maxspeed.isdigit():
                return float(maxspeed)
        elif isinstance(maxspeed, (int, float)):
            return float(maxspeed)
        
        # Default speed based on highway type
        highway_type = tags.get('highway', '')
        speed_map = {
            'motorway': 120.0,
            'trunk': 100.0,
            'primary': 80.0,
            'secondary': 60.0,
            'tertiary': 50.0,
            'residential': 30.0
        }
        return speed_map.get(highway_type, 50.0)
    
    def _extract_width(self, tags: Dict) -> float:
        """Extract road width from OSM tags"""
        width = tags.get('width', '')
        if isinstance(width, str) and width.replace('.', '').isdigit():
            return float(width)
        elif isinstance(width, (int, float)):
            return float(width)
        else:
            # Estimate based on lanes
            lanes = self._extract_lanes(tags)
            return lanes * 3.5  # 3.5m per lane
    
    def generate_sumo_network(self, network_data: Dict, output_file: str) -> bool:
        """
        Generate SUMO network file from OSM data
        
        Args:
            network_data: Processed network data
            output_file: Output SUMO .net.xml file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This is a simplified version - in production, use netconvert
            # For now, create a basic network structure
            
            network_xml = self._create_network_xml(network_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(network_xml)
            
            logger.info(f"SUMO network generated: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"SUMO network generation error: {e}")
            return False
    
    def _create_network_xml(self, network_data: Dict) -> str:
        """Create basic SUMO network XML structure"""
        # This is a simplified implementation
        # In production, use SUMO's netconvert tool with OSM data
        
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<net version="1.9" junctionCornerDetail="5" limitTurnSpeed="5.5" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,100.00,100.00" origBoundary="-180.00,-90.00,180.00,90.00" projParameter="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"/>
    
    <!-- Nodes (Junctions) -->
    <junction id="center" type="priority" x="50.0" y="50.0" incLanes="" intLanes="" shape="50.0,50.0"/>
    
    <!-- Edges (Roads) -->
    <edge id="north" from="center" to="north_end" priority="1">
        <lane id="north_0" index="0" speed="13.89" length="50.0" shape="50.0,50.0 50.0,0.0"/>
    </edge>
    <edge id="south" from="center" to="south_end" priority="1">
        <lane id="south_0" index="0" speed="13.89" length="50.0" shape="50.0,50.0 50.0,100.0"/>
    </edge>
    <edge id="east" from="center" to="east_end" priority="1">
        <lane id="east_0" index="0" speed="13.89" length="50.0" shape="50.0,50.0 100.0,50.0"/>
    </edge>
    <edge id="west" from="center" to="west_end" priority="1">
        <lane id="west_0" index="0" speed="13.89" length="50.0" shape="50.0,50.0 0.0,50.0"/>
    </edge>
    
    <!-- Traffic Lights -->
    <tlLogic id="center" type="static" programID="0" offset="0">
        <phase duration="31" state="GGrrrrGGrrrr"/>
        <phase duration="6" state="yyrrrryyrrrr"/>
        <phase duration="31" state="rrGGrrrrGGrr"/>
        <phase duration="6" state="rryyrrrryyrr"/>
        <phase duration="31" state="rrrrGGrrrrGG"/>
        <phase duration="6" state="rrrryyrrrryy"/>
        <phase duration="31" state="rrrrrrGGrrrr"/>
        <phase duration="6" state="rrrrrryyrrrr"/>
    </tlLogic>
</net>'''
        
        return xml_content
    
    def get_intersection_bounds(self, lat: float, lon: float, radius: float = 100) -> Tuple[float, float, float, float]:
        """
        Get bounding box for intersection area
        
        Args:
            lat: Latitude of intersection center
            lon: Longitude of intersection center
            radius: Search radius in meters
            
        Returns:
            Tuple of (min_lat, min_lon, max_lat, max_lon)
        """
        # Convert radius from meters to degrees (approximate)
        lat_delta = radius / 111000.0  # 1 degree ≈ 111km
        lon_delta = radius / (111000.0 * abs(np.cos(np.radians(lat))))
        
        return (
            lat - lat_delta,
            lon - lon_delta,
            lat + lat_delta,
            lon + lon_delta
        )
    
    def save_osm_data(self, osm_data: Dict, filename: str) -> bool:
        """
        Save OSM data to file
        
        Args:
            osm_data: OSM data to save
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(osm_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"OSM data saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"OSM data save error: {e}")
            return False
