#!/usr/bin/env python3
"""
SUMO Diagnostic Tool
Comprehensive error handling and debugging for SUMO GUI issues
"""

import os
import sys
import time
import subprocess
import traci
import json
from datetime import datetime

class SUMODiagnosticTool:
    """Comprehensive SUMO diagnostic and error handling tool"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.sumo_process = None
        
    def log_error(self, message, exception=None):
        """Log error with exception details"""
        error_msg = f"❌ ERROR: {message}"
        if exception:
            error_msg += f" | Exception: {str(exception)}"
        self.errors.append(error_msg)
        print(error_msg)
    
    def log_warning(self, message):
        """Log warning"""
        warning_msg = f"⚠️ WARNING: {message}"
        self.warnings.append(warning_msg)
        print(warning_msg)
    
    def log_info(self, message):
        """Log info"""
        info_msg = f"ℹ️ INFO: {message}"
        self.info.append(info_msg)
        print(info_msg)
    
    def check_system_requirements(self):
        """Check system requirements and SUMO installation"""
        print("🔍 Checking System Requirements...")
        print("=" * 50)
        
        # Check Python version
        python_version = sys.version_info
        self.log_info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check if TraCI is available
        try:
            import traci
            self.log_info("TraCI module is available")
        except ImportError as e:
            self.log_error("TraCI module not found", e)
            return False
        
        # Check SUMO_HOME environment variable
        sumo_home = os.environ.get('SUMO_HOME')
        if sumo_home:
            self.log_info(f"SUMO_HOME: {sumo_home}")
            sumo_gui_path = os.path.join(sumo_home, 'bin', 'sumo-gui.exe')
            if os.path.exists(sumo_gui_path):
                self.log_info(f"SUMO GUI found at: {sumo_gui_path}")
            else:
                self.log_error(f"SUMO GUI not found at: {sumo_gui_path}")
                return False
        else:
            self.log_warning("SUMO_HOME environment variable not set")
            # Try to find SUMO in common locations
            common_paths = [
                'C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui.exe',
                'C:\\Program Files\\Eclipse\\Sumo\\bin\\sumo-gui.exe',
                'sumo-gui.exe'
            ]
            
            sumo_found = False
            for path in common_paths:
                if os.path.exists(path):
                    self.log_info(f"SUMO GUI found at: {path}")
                    sumo_found = True
                    break
            
            if not sumo_found:
                self.log_error("SUMO GUI not found in common locations")
                return False
        
        return True
    
    def check_network_files(self):
        """Check SUMO network files for errors"""
        print("\n🔍 Checking Network Files...")
        print("=" * 50)
        
        required_files = [
            'fixed_working_network.net.xml',
            'working_traffic_routes.rou.xml',
            'fixed_working_traffic.sumocfg'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log_info(f"File exists: {file_path}")
                
                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    self.log_error(f"File is empty: {file_path}")
                else:
                    self.log_info(f"File size: {file_size} bytes")
                
                # Check if it's a valid XML file
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(file_path)
                    self.log_info(f"Valid XML: {file_path}")
                except ET.ParseError as e:
                    self.log_error(f"Invalid XML in {file_path}", e)
            else:
                self.log_error(f"File not found: {file_path}")
                return False
        
        return True
    
    def validate_network_xml(self):
        """Validate network XML structure"""
        print("\n🔍 Validating Network XML Structure...")
        print("=" * 50)
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse('fixed_working_network.net.xml')
            root = tree.getroot()
            
            # Check for required elements
            junctions = root.findall('junction')
            edges = root.findall('edge')
            connections = root.findall('connection')
            
            self.log_info(f"Found {len(junctions)} junctions")
            self.log_info(f"Found {len(edges)} edges")
            self.log_info(f"Found {len(connections)} connections")
            
            # Check for traffic light junction
            traffic_lights = [j for j in junctions if j.get('type') == 'traffic_light']
            if traffic_lights:
                self.log_info(f"Found {len(traffic_lights)} traffic light junctions")
                for tl in traffic_lights:
                    tl_id = tl.get('id')
                    inc_lanes = tl.get('incLanes', '')
                    int_lanes = tl.get('intLanes', '')
                    self.log_info(f"Traffic light {tl_id}: incLanes='{inc_lanes}', intLanes='{int_lanes}'")
            else:
                self.log_error("No traffic light junctions found")
                return False
            
            # Check for internal edges
            internal_edges = [e for e in edges if e.get('id', '').startswith(':')]
            if internal_edges:
                self.log_info(f"Found {len(internal_edges)} internal edges")
            else:
                self.log_warning("No internal edges found")
            
            return True
            
        except Exception as e:
            self.log_error("Failed to validate network XML", e)
            return False
    
    def test_sumo_command_line(self):
        """Test SUMO command line execution"""
        print("\n🔍 Testing SUMO Command Line...")
        print("=" * 50)
        
        try:
            # Find SUMO binary
            sumo_home = os.environ.get('SUMO_HOME')
            if sumo_home:
                sumo_binary = os.path.join(sumo_home, 'bin', 'sumo-gui.exe')
            else:
                sumo_binary = 'sumo-gui.exe'
            
            # Test SUMO version
            cmd = [sumo_binary, '--version']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_info(f"SUMO version: {result.stdout.strip()}")
            else:
                self.log_error(f"SUMO version check failed: {result.stderr}")
                return False
            
            # Test SUMO configuration validation
            cmd = [sumo_binary, '-c', 'fixed_working_traffic.sumocfg', '--check-config']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_info("SUMO configuration is valid")
            else:
                self.log_error(f"SUMO configuration validation failed: {result.stderr}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log_error("SUMO command timed out")
            return False
        except Exception as e:
            self.log_error("Failed to test SUMO command line", e)
            return False
    
    def start_sumo_with_diagnostics(self):
        """Start SUMO with comprehensive diagnostics"""
        print("\n🔍 Starting SUMO with Diagnostics...")
        print("=" * 50)
        
        try:
            # Find SUMO binary
            sumo_home = os.environ.get('SUMO_HOME')
            if sumo_home:
                sumo_binary = os.path.join(sumo_home, 'bin', 'sumo-gui.exe')
            else:
                sumo_binary = 'sumo-gui.exe'
            
            # Start SUMO with detailed logging
            cmd = [
                sumo_binary,
                '-c', 'fixed_working_traffic.sumocfg',
                '--remote-port', '8813',
                '--start',
                '--verbose'
            ]
            
            self.log_info(f"Starting SUMO with command: {' '.join(cmd)}")
            
            # Start SUMO process
            self.sumo_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for SUMO to start
            self.log_info("Waiting for SUMO to start...")
            time.sleep(8)
            
            # Check if process is still running
            if self.sumo_process.poll() is None:
                self.log_info("SUMO process is running")
            else:
                stdout, stderr = self.sumo_process.communicate()
                self.log_error(f"SUMO process exited with code {self.sumo_process.returncode}")
                self.log_error(f"STDOUT: {stdout}")
                self.log_error(f"STDERR: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            self.log_error("Failed to start SUMO", e)
            return False
    
    def test_traci_connection_with_retries(self):
        """Test TraCI connection with multiple retries and detailed error handling"""
        print("\n🔍 Testing TraCI Connection with Retries...")
        print("=" * 50)
        
        max_retries = 10
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.log_info(f"TraCI connection attempt {attempt + 1}/{max_retries}")
                
                # Try to connect
                traci.init(port=8813, numRetries=1)
                self.log_info("✅ TraCI connection successful!")
                
                # Test basic functionality
                sim_time = traci.simulation.getTime()
                self.log_info(f"Simulation time: {sim_time}")
                
                vehicle_ids = traci.vehicle.getIDList()
                self.log_info(f"Vehicles: {len(vehicle_ids)}")
                
                tl_ids = traci.trafficlight.getIDList()
                self.log_info(f"Traffic lights: {tl_ids}")
                
                # Test simulation step
                traci.simulationStep()
                self.log_info("Simulation step successful")
                
                # Close connection
                traci.close()
                self.log_info("TraCI connection closed successfully")
                
                return True
                
            except Exception as e:
                self.log_warning(f"TraCI connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    self.log_info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.log_error("All TraCI connection attempts failed", e)
                    return False
        
        return False
    
    def run_complete_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🔍 SUMO Complete Diagnostic Tool")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Run all diagnostic checks
        checks = [
            ("System Requirements", self.check_system_requirements),
            ("Network Files", self.check_network_files),
            ("Network XML Validation", self.validate_network_xml),
            ("SUMO Command Line", self.test_sumo_command_line),
            ("SUMO Startup", self.start_sumo_with_diagnostics),
            ("TraCI Connection", self.test_traci_connection_with_retries)
        ]
        
        results = {}
        
        for check_name, check_func in checks:
            print(f"\n{'='*60}")
            print(f"Running: {check_name}")
            print('='*60)
            
            try:
                result = check_func()
                results[check_name] = result
                if result:
                    print(f"✅ {check_name}: PASSED")
                else:
                    print(f"❌ {check_name}: FAILED")
            except Exception as e:
                self.log_error(f"Error in {check_name}", e)
                results[check_name] = False
                print(f"❌ {check_name}: ERROR")
        
        # Generate summary report
        self.generate_summary_report(results)
        
        return results
    
    def generate_summary_report(self, results):
        """Generate summary report"""
        print("\n" + "="*60)
        print("📊 DIAGNOSTIC SUMMARY REPORT")
        print("="*60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        print(f"Total Checks: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for check_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {check_name}")
        
        print("\n📝 Errors Found:")
        for error in self.errors:
            print(f"  {error}")
        
        print("\n⚠️ Warnings:")
        for warning in self.warnings:
            print(f"  {warning}")
        
        print("\nℹ️ Info:")
        for info in self.info:
            print(f"  {info}")
        
        # Save report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'summary': {
                'total_checks': total,
                'passed': passed,
                'failed': total - passed,
                'success_rate': (passed/total)*100
            }
        }
        
        with open('sumo_diagnostic_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Full report saved to: sumo_diagnostic_report.json")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.sumo_process:
            try:
                self.sumo_process.terminate()
                self.sumo_process.wait(timeout=5)
            except:
                try:
                    self.sumo_process.kill()
                except:
                    pass

def main():
    """Main function"""
    diagnostic = SUMODiagnosticTool()
    
    try:
        results = diagnostic.run_complete_diagnostic()
        
        # Check if all tests passed
        if all(results.values()):
            print("\n🎉 All diagnostic tests passed! SUMO should be working correctly.")
        else:
            print("\n⚠️ Some diagnostic tests failed. Check the report above for details.")
            
    except KeyboardInterrupt:
        print("\n🛑 Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
    finally:
        diagnostic.cleanup()

if __name__ == "__main__":
    main()
