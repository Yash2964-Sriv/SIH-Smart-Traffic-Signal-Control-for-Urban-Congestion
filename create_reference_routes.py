#!/usr/bin/env python3
"""
Create routes for the reference OSM network
"""

import xml.etree.ElementTree as ET

def create_reference_routes():
    """Create routes for the OSM network"""
    print("🛣️ Creating routes for OSM network...")
    
    # Read the network file to get edge IDs
    try:
        tree = ET.parse("real_traffic_output/reference_osm_network.net.xml")
        root = tree.getroot()
        
        # Find all edge IDs
        edge_ids = []
        for edge in root.findall(".//edge"):
            edge_id = edge.get("id")
            if edge_id and not edge_id.startswith(":"):  # Skip internal edges
                edge_ids.append(edge_id)
        
        print(f"Found {len(edge_ids)} edges in network")
        
        if len(edge_ids) < 2:
            print("❌ Not enough edges for routes")
            return False
        
        # Create routes file
        routes = ET.Element("routes")
        
        # Add vehicle types
        vtypes = [
            ("passenger", "red", "car", 4.5, 1.8, 1.0, 2.5, 4.5),
            ("truck", "blue", "truck", 8.0, 2.5, 0.8, 2.0, 3.5),
            ("bus", "green", "bus", 12.0, 2.5, 0.6, 1.5, 3.0),
            ("motorcycle", "yellow", "motorcycle", 2.2, 1.0, 1.5, 3.0, 5.0),
            ("taxi", "orange", "taxi", 4.5, 1.8, 1.2, 2.8, 4.8),
            ("emergency", "red", "emergency", 5.5, 2.0, 1.8, 3.5, 6.0)
        ]
        
        for vtype_id, color, vclass, length, width, accel, decel, max_speed in vtypes:
            vtype = ET.SubElement(routes, "vType")
            vtype.set("id", vtype_id)
            vtype.set("color", color)
            vtype.set("vClass", vclass)
            vtype.set("length", str(length))
            vtype.set("width", str(width))
            vtype.set("accel", str(accel))
            vtype.set("decel", str(decel))
            vtype.set("maxSpeed", str(max_speed))
        
        # Create routes using available edges
        route_count = 0
        for i in range(min(50, len(edge_ids) - 1)):  # Create 50 routes
            if i + 1 < len(edge_ids):
                route = ET.SubElement(routes, "route")
                route.set("id", f"route_{i}")
                route.set("edges", f"{edge_ids[i]} {edge_ids[i+1]}")
                
                # Add vehicles to this route
                for j in range(3):  # 3 vehicles per route
                    vehicle = ET.SubElement(routes, "vehicle")
                    vehicle.set("id", f"veh_{route_count}")
                    vehicle.set("type", vtypes[route_count % len(vtypes)][0])
                    vehicle.set("route", f"route_{i}")
                    vehicle.set("depart", str(i * 2 + j * 0.5))
                    vehicle.set("departLane", "best")
                    vehicle.set("departSpeed", "max")
                    route_count += 1
        
        # Save routes file
        tree = ET.ElementTree(routes)
        ET.indent(tree, space="  ", level=0)
        tree.write("real_traffic_output/reference_routes.rou.xml", encoding="utf-8", xml_declaration=True)
        
        print(f"✅ Created {route_count} vehicles in routes file")
        return True
        
    except Exception as e:
        print(f"❌ Error creating routes: {e}")
        return False

if __name__ == "__main__":
    create_reference_routes()
