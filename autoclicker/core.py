"""
Core autoclicker logic module.

This module contains the AutoClicker class which handles the main
autoclicking functionality including threading and click execution.
"""

import json
import random
import threading
import time
from datetime import datetime

from pynput.mouse import Controller as MouseController, Button

from .models import ClickPoint


class AutoClicker:
    """Main autoclicker logic"""
    
    def __init__(self):
        self.click_points = []
        self.mouse = MouseController()
        self.running = False
        self.start_delay = 8.0
        self.loop_count = 0  # 0 = infinite
        self.current_loop = 0
        self.click_count = 0
        self.on_status_change = None
        self.on_click = None
        self.on_loop_complete = None
        self.thread = None
        self.stop_requested = False
        self.verify_position = True  # Re-check position before clicking
        self.debug_mode = False  # Print debug info to console
        
    def add_point(self, point):
        """Add a click point"""
        self.click_points.append(point)
        
    def remove_point(self, index):
        """Remove a click point by index"""
        if 0 <= index < len(self.click_points):
            del self.click_points[index]
            
    def clear_points(self):
        """Clear all click points"""
        self.click_points.clear()
        
    def start(self):
        """Start the autoclicker in a separate thread"""
        if self.running or not self.click_points:
            return False
        self.running = True
        self.stop_requested = False
        self.current_loop = 0
        self.click_count = 0
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True
        
    def stop(self):
        """Stop the autoclicker"""
        self.stop_requested = True
        
    def _run(self):
        """Main autoclicker loop"""
        try:
            # Initial delay
            if self.on_status_change:
                self.on_status_change(f"Starting in {self.start_delay}s...")
            time.sleep(self.start_delay)
            
            enabled_points = [p for p in self.click_points if p.enabled]
            if not enabled_points:
                self.running = False
                if self.on_status_change:
                    self.on_status_change("No enabled click points!")
                return
            
            while self.running and not self.stop_requested:
                self.current_loop += 1
                
                # Check loop count limit
                if self.loop_count > 0 and self.current_loop > self.loop_count:
                    break
                
                if self.on_status_change:
                    self.on_status_change(f"Running - Loop {self.current_loop}")
                
                for i, point in enumerate(enabled_points):
                    if self.stop_requested:
                        break
                        
                    if not point.enabled:
                        continue
                    
                    # Get position with randomization
                    pos = point.get_click_position()
                    
                    # Move and click
                    self.mouse.position = pos
                    time.sleep(0.05)  # Small delay before click
                    
                    # Verify position before clicking (prevents drift)
                    if self.verify_position:
                        actual_pos = self.mouse.position
                        if actual_pos != pos:
                            if self.debug_mode:
                                print(f"[DEBUG] Position drift detected: intended {pos}, actual {actual_pos}")
                            self.mouse.position = pos
                            time.sleep(0.01)
                    
                    self.mouse.click(Button.left)
                    self.click_count += 1
                    
                    if self.debug_mode:
                        final_pos = self.mouse.position
                        print(f"[DEBUG] Click #{self.click_count} at {final_pos} (target: {pos})")
                    
                    if self.on_click:
                        self.on_click(i, pos, self.click_count)
                    
                    # Wait for the specified delay before next click
                    if not self.stop_requested:
                        # Add small randomization to delay (±5%)
                        delay_variation = point.delay * 0.05
                        actual_delay = point.delay + random.uniform(-delay_variation, delay_variation)
                        time.sleep(max(0.1, actual_delay))
                
                if self.on_loop_complete:
                    self.on_loop_complete(self.current_loop)
                    
        except Exception as e:
            if self.on_status_change:
                self.on_status_change(f"Error: {str(e)}")
        finally:
            self.running = False
            if self.on_status_change:
                self.on_status_change("Stopped")
                
    def save_config(self, filepath, name="", description=""):
        """Save configuration to JSON file with name and description"""
        config = {
            'name': name,
            'description': description,
            'start_delay': self.start_delay,
            'loop_count': self.loop_count,
            'click_points': [p.to_dict() for p in self.click_points],
            'saved_at': datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
            
    def load_config(self, filepath):
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        self.start_delay = config.get('start_delay', 3.0)
        self.loop_count = config.get('loop_count', 0)
        self.click_points = [ClickPoint.from_dict(p) for p in config.get('click_points', [])]
        return config
