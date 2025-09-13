#!/usr/bin/env python3
"""
Create Working SUMO Network for Master AI Traffic Control
Generates a proper SUMO network based on real traffic video analysis
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def create_working_sumo_network():
    """Create a working SUMO network for traffic control"""
    print("🏗️ Creating Working SUMO Network for Master AI...")
    
    # Load video analysis data
    try:
        with open('real_traffic_analysis.json', 'r') as f:
            analysis_data = json.load(f)
        print("✅ Loaded video analysis data")
    except:
        print("⚠️ Using default traffic patterns")
        analysis_data = {
            'traffic_patterns': {
                'avg_vehicles_per_frame': 47.6,
                'traffic_flow_rate': 200
            },
            'timing_data': {
                'avg_travel_time': 18.28
            }
        }
    
    # Create network XML
    create_network_xml(analysis_data)
    
    # Create routes XML
    create_routes_xml(analysis_data)
    
    # Create traffic lights XML
    create_traffic_lights_xml()
    
    # Create SUMO config
    create_sumo_config()
    
    print("✅ Working SUMO network created successfully!")

def create_network_xml(analysis_data):
    """Create SUMO network XML file"""
    print("📐 Creating network XML...")
    
    # Create root element
    net = ET.Element('net')
    net.set('version', '1.9')
    net.set('junctionCornerDetail', '5')
    net.set('limitTurnSpeed', '5.5')
    
    # Add location
    location = ET.SubElement(net, 'location')
    location.set('netOffset', '0.00,0.00')
    location.set('convBoundary', '0.00,0.00,100.00,100.00')
    location.set('origBoundary', '-10000000000.00,-10000000000.00,10000000000.00,10000000000.00')
    location.set('projParameter', '!')
    
    # Add edge types
    edge_type = ET.SubElement(net, 'edgeType')
    edge_type.set('id', 'highway')
    edge_type.set('priority', '1')
    edge_type.set('numLanes', '2')
    edge_type.set('speed', '13.89')
    
    lane_type = ET.SubElement(edge_type, 'laneType')
    lane_type.set('id', 'highway')
    lane_type.set('speed', '13.89')
    lane_type.set('length', '100.00')
    lane_type.set('width', '3.50')
    
    # Add junctions
    junctions = [
        {'id': 'I1', 'x': '50.00', 'y': '50.00', 'type': 'traffic_light'},
        {'id': 'N1', 'x': '50.00', 'y': '100.00', 'type': 'priority'},
        {'id': 'S1', 'x': '50.00', 'y': '0.00', 'type': 'priority'},
        {'id': 'E1', 'x': '100.00', 'y': '50.00', 'type': 'priority'},
        {'id': 'W1', 'x': '0.00', 'y': '50.00', 'type': 'priority'}
    ]
    
    for junction in junctions:
        j = ET.SubElement(net, 'junction')
        j.set('id', junction['id'])
        j.set('x', junction['x'])
        j.set('y', junction['y'])
        j.set('type', junction['type'])
        j.set('incLanes', '')
        j.set('intLanes', '')
        j.set('shape', f"{junction['x']},{junction['y']}")
    
    # Add edges
    edges = [
        {'id': 'N1_to_I1', 'from': 'N1', 'to': 'I1', 'priority': '1', 'numLanes': '2', 'speed': '13.89'},
        {'id': 'I1_to_S1', 'from': 'I1', 'to': 'S1', 'priority': '1', 'numLanes': '2', 'speed': '13.89'},
        {'id': 'E1_to_I1', 'from': 'E1', 'to': 'I1', 'priority': '1', 'numLanes': '2', 'speed': '13.89'},
        {'id': 'I1_to_W1', 'from': 'I1', 'to': 'W1', 'priority': '1', 'numLanes': '2', 'speed': '13.89'}
    ]
    
    for edge in edges:
        e = ET.SubElement(net, 'edge')
        e.set('id', edge['id'])
        e.set('from', edge['from'])
        e.set('to', edge['to'])
        e.set('priority', edge['priority'])
        e.set('numLanes', edge['numLanes'])
        e.set('speed', edge['speed'])
        
        # Add lane
        lane = ET.SubElement(e, 'lane')
        lane.set('id', f"{edge['id']}_0")
        lane.set('index', '0')
        lane.set('speed', edge['speed'])
        lane.set('length', '50.00')
        lane.set('width', '3.50')
        lane.set('shape', f"0.00,0.00 50.00,0.00")
    
    # Add connections
    connections = [
        {'from': 'N1_to_I1', 'to': 'I1_to_S1', 'fromLane': '0', 'toLane': '0', 'dir': 's', 'state': 'M'},
        {'from': 'E1_to_I1', 'to': 'I1_to_W1', 'fromLane': '0', 'toLane': '0', 'dir': 'l', 'state': 'M'},
        {'from': 'I1_to_S1', 'to': 'N1_to_I1', 'fromLane': '0', 'toLane': '0', 'dir': 's', 'state': 'M'},
        {'from': 'I1_to_W1', 'to': 'E1_to_I1', 'fromLane': '0', 'toLane': '0', 'dir': 'l', 'state': 'M'}
    ]
    
    for conn in connections:
        c = ET.SubElement(net, 'connection')
        c.set('from', conn['from'])
        c.set('to', conn['to'])
        c.set('fromLane', conn['fromLane'])
        c.set('toLane', conn['toLane'])
        c.set('dir', conn['dir'])
        c.set('state', conn['state'])
    
    # Write network file
    tree = ET.ElementTree(net)
    ET.indent(tree, space="  ", level=0)
    tree.write('working_network.net.xml', encoding='utf-8', xml_declaration=True)
    print("✅ Network XML created: working_network.net.xml")

def create_routes_xml(analysis_data):
    """Create SUMO routes XML file"""
    print("🛣️ Creating routes XML...")
    
    # Get traffic data
    avg_vehicles = analysis_data.get('traffic_patterns', {}).get('avg_vehicles_per_frame', 47.6)
    flow_rate = analysis_data.get('traffic_patterns', {}).get('traffic_flow_rate', 200)
    
    # Create root element
    routes = ET.Element('routes')
    
    # Add vehicle types
    vtype_car = ET.SubElement(routes, 'vType')
    vtype_car.set('id', 'car')
    vtype_car.set('accel', '2.6')
    vtype_car.set('decel', '4.5')
    vtype_car.set('sigma', '0.5')
    vtype_car.set('length', '5.0')
    vtype_car.set('maxSpeed', '13.89')
    
    # Add routes
    route_definitions = [
        {'id': 'route_NS', 'edges': 'N1_to_I1 I1_to_S1'},
        {'id': 'route_SN', 'edges': 'I1_to_S1 N1_to_I1'},
        {'id': 'route_EW', 'edges': 'E1_to_I1 I1_to_W1'},
        {'id': 'route_WE', 'edges': 'I1_to_W1 E1_to_I1'}
    ]
    
    for route in route_definitions:
        r = ET.SubElement(routes, 'route')
        r.set('id', route['id'])
        r.set('edges', route['edges'])
    
    # Add vehicle flows based on real traffic data
    flows = [
        {'id': 'flow_NS', 'route': 'route_NS', 'begin': '0', 'end': '3600', 'vehsPerHour': str(int(flow_rate * 0.3))},
        {'id': 'flow_SN', 'route': 'route_SN', 'begin': '0', 'end': '3600', 'vehsPerHour': str(int(flow_rate * 0.3))},
        {'id': 'flow_EW', 'route': 'route_EW', 'begin': '0', 'end': '3600', 'vehsPerHour': str(int(flow_rate * 0.2))},
        {'id': 'flow_WE', 'route': 'route_WE', 'begin': '0', 'end': '3600', 'vehsPerHour': str(int(flow_rate * 0.2))}
    ]
    
    for flow in flows:
        f = ET.SubElement(routes, 'flow')
        f.set('id', flow['id'])
        f.set('route', flow['route'])
        f.set('begin', flow['begin'])
        f.set('end', flow['end'])
        f.set('vehsPerHour', flow['vehsPerHour'])
        f.set('type', 'car')
    
    # Write routes file
    tree = ET.ElementTree(routes)
    ET.indent(tree, space="  ", level=0)
    tree.write('working_routes.rou.xml', encoding='utf-8', xml_declaration=True)
    print("✅ Routes XML created: working_routes.rou.xml")

def create_traffic_lights_xml():
    """Create traffic lights XML file"""
    print("🚦 Creating traffic lights XML...")
    
    # Create root element
    tl_logic = ET.Element('tlLogic')
    tl_logic.set('id', 'I1')
    tl_logic.set('type', 'static')
    tl_logic.set('programID', '0')
    tl_logic.set('offset', '0')
    
    # Add phases
    phases = [
        {'state': 'GGrr', 'duration': '30'},
        {'state': 'yyrr', 'duration': '3'},
        {'state': 'rrGG', 'duration': '30'},
        {'state': 'rryy', 'duration': '3'}
    ]
    
    for phase in phases:
        p = ET.SubElement(tl_logic, 'phase')
        p.set('state', phase['state'])
        p.set('duration', phase['duration'])
    
    # Write traffic lights file
    tree = ET.ElementTree(tl_logic)
    ET.indent(tree, space="  ", level=0)
    tree.write('working_traffic_lights.xml', encoding='utf-8', xml_declaration=True)
    print("✅ Traffic lights XML created: working_traffic_lights.xml")

def create_sumo_config():
    """Create SUMO configuration file"""
    print("⚙️ Creating SUMO configuration...")
    
    # Create root element
    configuration = ET.Element('configuration')
    configuration.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    configuration.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/sumoConfiguration.xsd')
    
    # Add input
    input_elem = ET.SubElement(configuration, 'input')
    
    net_file = ET.SubElement(input_elem, 'net-file')
    net_file.set('value', 'working_network.net.xml')
    
    route_files = ET.SubElement(input_elem, 'route-files')
    route_files.set('value', 'working_routes.rou.xml')
    
    # Add time
    time_elem = ET.SubElement(configuration, 'time')
    
    begin = ET.SubElement(time_elem, 'begin')
    begin.set('value', '0')
    
    end = ET.SubElement(time_elem, 'end')
    end.set('value', '3600')
    
    # Add processing
    processing = ET.SubElement(configuration, 'processing')
    
    ignore_junction_blocking = ET.SubElement(processing, 'ignore-junction-blocking')
    ignore_junction_blocking.set('value', 'true')
    
    # Write config file
    tree = ET.ElementTree(configuration)
    ET.indent(tree, space="  ", level=0)
    tree.write('working_traffic.sumocfg', encoding='utf-8', xml_declaration=True)
    print("✅ SUMO configuration created: working_traffic.sumocfg")

if __name__ == "__main__":
    create_working_sumo_network()
