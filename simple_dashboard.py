#!/usr/bin/env python3
"""
Simple Dashboard with AI Simulation Integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from dashboard_ai_integration import DashboardAIIntegration

class SimpleDashboard:
    """Simple dashboard with AI simulation controls"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Traffic Control Dashboard")
        self.root.geometry("600x400")
        
        # Initialize AI integration
        self.ai_integration = DashboardAIIntegration()
        self.simulation_running = False
        
        # Create GUI
        self.create_widgets()
        
        # Start status monitoring
        self.monitor_status()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Title
        title_label = tk.Label(self.root, text="AI Traffic Control Dashboard", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.root, text="Simulation Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Not Running", 
                                   fg="red", font=("Arial", 12))
        self.status_label.pack()
        
        # Control frame
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Start button
        self.start_button = tk.Button(control_frame, text="Start AI Simulation", 
                                    command=self.start_simulation,
                                    bg="green", fg="white", font=("Arial", 12))
        self.start_button.pack(side="left", padx=5)
        
        # Stop button
        self.stop_button = tk.Button(control_frame, text="Stop Simulation", 
                                   command=self.stop_simulation,
                                   bg="red", fg="white", font=("Arial", 12),
                                   state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Performance frame
        perf_frame = ttk.LabelFrame(self.root, text="Performance Metrics", padding=10)
        perf_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Performance labels
        self.vehicles_label = tk.Label(perf_frame, text="Total Vehicles: 0")
        self.vehicles_label.pack(anchor="w")
        
        self.queue_label = tk.Label(perf_frame, text="Average Queue Length: 0")
        self.queue_label.pack(anchor="w")
        
        self.efficiency_label = tk.Label(perf_frame, text="Efficiency Score: 0%")
        self.efficiency_label.pack(anchor="w")
        
        self.decisions_label = tk.Label(perf_frame, text="AI Decisions Made: 0")
        self.decisions_label.pack(anchor="w")
        
        # Info frame
        info_frame = ttk.LabelFrame(self.root, text="Information", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        info_text = tk.Text(info_frame, height=4, wrap="word")
        info_text.pack(fill="x")
        
        info_content = """This dashboard controls an AI-powered traffic simulation based on real traffic video analysis.
The AI uses reinforcement learning to control traffic lights intelligently.
Click 'Start AI Simulation' to begin the simulation with SUMO GUI."""
        
        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")
    
    def start_simulation(self):
        """Start AI simulation"""
        def run_simulation():
            try:
                if self.ai_integration.start_simulation():
                    self.simulation_running = True
                    self.root.after(0, self.update_ui_running)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to start simulation"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Simulation error: {e}"))
        
        # Run in separate thread
        thread = threading.Thread(target=run_simulation)
        thread.daemon = True
        thread.start()
    
    def stop_simulation(self):
        """Stop AI simulation"""
        try:
            if self.ai_integration.stop_simulation():
                self.simulation_running = False
                self.update_ui_stopped()
            else:
                messagebox.showerror("Error", "Failed to stop simulation")
        except Exception as e:
            messagebox.showerror("Error", f"Stop error: {e}")
    
    def update_ui_running(self):
        """Update UI for running state"""
        self.status_label.config(text="Running", fg="green")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
    
    def update_ui_stopped(self):
        """Update UI for stopped state"""
        self.status_label.config(text="Not Running", fg="red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def monitor_status(self):
        """Monitor simulation status and update performance metrics"""
        try:
            if self.simulation_running:
                # Update performance metrics
                performance = self.ai_integration.get_performance_data()
                if performance:
                    self.vehicles_label.config(text=f"Total Vehicles: {performance.get('total_vehicles_processed', 0)}")
                    self.queue_label.config(text=f"Average Queue Length: {performance.get('average_queue_length', 0):.2f}")
                    self.efficiency_label.config(text=f"Efficiency Score: {performance.get('average_efficiency_score', 0):.2f}%")
                    self.decisions_label.config(text=f"AI Decisions Made: {performance.get('ai_decisions_made', 0)}")
                
                # Check if simulation is still running
                status = self.ai_integration.get_simulation_status()
                if not status['sumo_running'] or not status['ai_running']:
                    self.simulation_running = False
                    self.update_ui_stopped()
        
        except Exception as e:
            print(f"Status monitoring error: {e}")
        
        # Schedule next update
        self.root.after(2000, self.monitor_status)

def main():
    """Main function"""
    root = tk.Tk()
    dashboard = SimpleDashboard(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (600 // 2)
    y = (root.winfo_screenheight() // 2) - (400 // 2)
    root.geometry(f"600x400+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
