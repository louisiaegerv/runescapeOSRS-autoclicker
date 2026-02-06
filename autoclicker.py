#!/usr/bin/env python3
"""
OSRS AutoClicker - A feature-rich autoclicker for AFK skilling
Features:
- Add multiple click locations with individual delays
- Hotkey-based coordinate capture (F6 to capture cursor position)
- Save/load click configurations
- Randomization options for anti-detection
- Visual feedback and status indicators
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import threading
import os
import random
from datetime import datetime
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener, Key, KeyCode

# Default configs directory
CONFIGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs")

def get_configs_dir():
    """Get or create the configs directory"""
    if not os.path.exists(CONFIGS_DIR):
        os.makedirs(CONFIGS_DIR)
    return CONFIGS_DIR


class ClickPoint:
    """Represents a single click location with its settings"""
    def __init__(self, x=0, y=0, delay=8.0, randomize=False, random_range=0):
        self.x = x
        self.y = y
        self.delay = delay  # Delay AFTER this click (before next click)
        self.randomize = randomize
        self.random_range = random_range  # Random offset range in pixels
        self.enabled = True
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'delay': self.delay,
            'randomize': self.randomize,
            'random_range': self.random_range,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        cp = cls(
            x=data.get('x', 0),
            y=data.get('y', 0),
            delay=data.get('delay', 8.0),
            randomize=data.get('randomize', False),
            random_range=data.get('random_range', 0)
        )
        cp.enabled = data.get('enabled', True)
        return cp
    
    def get_click_position(self):
        """Get the actual click position with randomization if enabled"""
        if self.randomize:
            offset_x = random.randint(-self.random_range, self.random_range)
            offset_y = random.randint(-self.random_range, self.random_range)
            return (self.x + offset_x, self.y + offset_y)
        return (self.x, self.y)


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


class HotkeyListener:
    """Global hotkey listener"""
    def __init__(self):
        self.listener = None
        self.capture_callback = None  # F6 - enter rapid add mode
        self.start_callback = None    # F7 - start
        self.stop_callback = None     # F8 - stop
        self.number_callback = None   # 0-9 in rapid add mode
        self.exit_capture_callback = None  # F9/ESC - exit rapid add mode
        self.capturing = False
        self.rapid_add_mode = False
        
    def start(self):
        """Start the global hotkey listener"""
        self.listener = Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        
    def stop(self):
        """Stop the listener"""
        if self.listener:
            self.listener.stop()
            
    def _on_press(self, key):
        """Handle key press"""
        try:
            # F6 - Enter rapid add mode (or add point if already in mode)
            if key == Key.f6:
                if self.capture_callback:
                    if not self.rapid_add_mode:
                        self.rapid_add_mode = True
                        self.capture_callback(start_mode=True)
                    else:
                        # Already in rapid add mode, use default delay (3s)
                        if self.number_callback:
                            self.number_callback(3)
                return
            
            # F9 or ESC - Exit rapid add mode
            if key == Key.f9 or key == Key.esc:
                if self.rapid_add_mode and self.exit_capture_callback:
                    self.rapid_add_mode = False
                    self.exit_capture_callback()
                return
            
            # Number keys 0-9 (only in rapid add mode)
            if self.rapid_add_mode and self.number_callback:
                # Handle both top row numbers and numpad
                delay = None
                if hasattr(key, 'char') and key.char and key.char.isdigit():
                    delay = int(key.char)
                elif key == KeyCode.from_vk(96):  # numpad 0
                    delay = 0
                elif key == KeyCode.from_vk(97):  # numpad 1
                    delay = 1
                elif key == KeyCode.from_vk(98):  # numpad 2
                    delay = 2
                elif key == KeyCode.from_vk(99):  # numpad 3
                    delay = 3
                elif key == KeyCode.from_vk(100):  # numpad 4
                    delay = 4
                elif key == KeyCode.from_vk(101):  # numpad 5
                    delay = 5
                elif key == KeyCode.from_vk(102):  # numpad 6
                    delay = 6
                elif key == KeyCode.from_vk(103):  # numpad 7
                    delay = 7
                elif key == KeyCode.from_vk(104):  # numpad 8
                    delay = 8
                elif key == KeyCode.from_vk(105):  # numpad 9
                    delay = 9
                
                if delay is not None:
                    # 0 = 10 seconds for convenience
                    actual_delay = 10 if delay == 0 else delay
                    self.number_callback(actual_delay)
                return
            
            # F7 - Start autoclicker (only when not in rapid add mode)
            if key == Key.f7 and not self.rapid_add_mode:
                if self.start_callback:
                    self.start_callback()
            # F8 - Stop autoclicker
            elif key == Key.f8:
                if self.stop_callback:
                    self.stop_callback()
        except Exception:
            pass
            
    def _on_release(self, key):
        """Handle key release"""
        pass


class AutoClickerGUI:
    """Main GUI application"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSRS AutoClicker")
        self.root.geometry("700x600")
        self.root.minsize(650, 500)
        
        # Set icon and styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize autoclicker
        self.autoclicker = AutoClicker()
        self.autoclicker.on_status_change = self._on_status_change
        self.autoclicker.on_click = self._on_click
        
        # Hotkey listener
        self.hotkey_listener = HotkeyListener()
        self.hotkey_listener.capture_callback = self._on_rapid_add_mode
        self.hotkey_listener.number_callback = self._on_number_key
        self.hotkey_listener.exit_capture_callback = self._on_exit_rapid_add
        self.hotkey_listener.start_callback = self._start_autoclicker
        self.hotkey_listener.stop_callback = self._stop_autoclicker
        
        # Rapid add mode state
        self.rapid_add_active = False
        
        # Mouse controller for capture
        self.mouse = MouseController()
        
        # Track currently loaded config for quick save
        self.current_config_path = None
        self.current_config_name = None
        
        # Build GUI
        self._build_gui()
        
        # Load saved configs list
        self._refresh_config_list()
        
        # Start hotkey listener
        self.hotkey_listener.start()
        
        # Update loop for status
        self._schedule_updates()
        
    def _build_gui(self):
        """Build the GUI components"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Click points list row
        main_frame.rowconfigure(3, weight=1)  # Config list row
        
        # ===== Header Section =====
        header_frame = ttk.LabelFrame(main_frame, text="Hotkeys", padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="F6", font=('Arial', 10, 'bold'), 
                 foreground='#0066cc').grid(row=0, column=0, padx=(0, 5))
        ttk.Label(header_frame, text="= Rapid Add Mode").grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(header_frame, text="0-9", font=('Arial', 10, 'bold'), 
                 foreground='#ff6600').grid(row=0, column=2, padx=(0, 5))
        ttk.Label(header_frame, text="= Delay (sec)").grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(header_frame, text="F9", font=('Arial', 10, 'bold'), 
                 foreground='#9900cc').grid(row=0, column=4, padx=(0, 5))
        ttk.Label(header_frame, text="= Exit Rapid Add").grid(row=0, column=5, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(header_frame, text="F7", font=('Arial', 10, 'bold'), 
                 foreground='#009900').grid(row=0, column=6, padx=(0, 5))
        ttk.Label(header_frame, text="= Start").grid(row=0, column=7, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(header_frame, text="F8", font=('Arial', 10, 'bold'), 
                 foreground='#cc0000').grid(row=0, column=8, padx=(0, 5))
        ttk.Label(header_frame, text="= Stop").grid(row=0, column=9, sticky=tk.W)
        
        # ===== Settings Section =====
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Start delay
        ttk.Label(settings_frame, text="Start Delay (s):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_delay_var = tk.DoubleVar(value=3.0)
        ttk.Spinbox(settings_frame, from_=0.5, to=30.0, increment=0.5, 
                   textvariable=self.start_delay_var, width=10).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(settings_frame, text="Time before first click", foreground='gray').grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Loop count
        ttk.Label(settings_frame, text="Loop Count:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.loop_count_var = tk.IntVar(value=0)
        ttk.Spinbox(settings_frame, from_=0, to=9999, increment=1, 
                   textvariable=self.loop_count_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        ttk.Label(settings_frame, text="0 = Infinite loops", foreground='gray').grid(row=1, column=2, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Verify position checkbox (prevents drift)
        self.verify_pos_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Verify click position (prevents drift)", 
                       variable=self.verify_pos_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Debug mode checkbox
        self.debug_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Debug mode (show actual click coords in console)", 
                       variable=self.debug_mode_var).grid(row=3, column=0, columnspan=3, sticky=tk.W)
        
        # ===== Click Points Section =====
        points_frame = ttk.LabelFrame(main_frame, text="Click Points", padding="10")
        points_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        points_frame.columnconfigure(0, weight=1)
        
        # Buttons row
        btn_frame = ttk.Frame(points_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(btn_frame, text="➕ Add Point (F6)", command=self._capture_cursor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ Remove Selected", command=self._remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📋 Clear All", command=self._clear_all).pack(side=tk.LEFT)
        
        # Treeview for click points
        tree_frame = ttk.Frame(points_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ('#', 'X', 'Y', 'Delay', 'Random', 'Range', 'Enabled')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        self.tree.heading('#', text='#')
        self.tree.heading('X', text='X')
        self.tree.heading('Y', text='Y')
        self.tree.heading('Delay', text='Delay (s)')
        self.tree.heading('Random', text='Randomize')
        self.tree.heading('Range', text='±Pixels')
        self.tree.heading('Enabled', text='On')
        
        self.tree.column('#', width=30, anchor='center')
        self.tree.column('X', width=60, anchor='center')
        self.tree.column('Y', width=60, anchor='center')
        self.tree.column('Delay', width=80, anchor='center')
        self.tree.column('Random', width=70, anchor='center')
        self.tree.column('Range', width=70, anchor='center')
        self.tree.column('Enabled', width=50, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click and Enter to edit
        self.tree.bind('<Double-1>', self._on_tree_double_click)
        self.tree.bind('<Return>', self._on_tree_double_click)
        
        # ===== Config Manager Section =====
        config_frame = ttk.LabelFrame(main_frame, text="Saved Configurations", padding="10")
        config_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        config_frame.columnconfigure(0, weight=1)
        config_frame.rowconfigure(1, weight=1)
        
        # Config list treeview
        config_tree_frame = ttk.Frame(config_frame)
        config_tree_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        config_tree_frame.columnconfigure(0, weight=1)
        config_tree_frame.rowconfigure(0, weight=1)
        
        config_columns = ('Name', 'Description', 'Points', 'Saved')
        self.config_tree = ttk.Treeview(config_tree_frame, columns=config_columns, show='headings', height=4)
        
        self.config_tree.heading('Name', text='Name')
        self.config_tree.heading('Description', text='Description')
        self.config_tree.heading('Points', text='Points')
        self.config_tree.heading('Saved', text='Saved Date')
        
        self.config_tree.column('Name', width=150, anchor='w')
        self.config_tree.column('Description', width=250, anchor='w')
        self.config_tree.column('Points', width=50, anchor='center')
        self.config_tree.column('Saved', width=120, anchor='center')
        
        config_scrollbar = ttk.Scrollbar(config_tree_frame, orient=tk.VERTICAL, command=self.config_tree.yview)
        self.config_tree.configure(yscrollcommand=config_scrollbar.set)
        
        self.config_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        config_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click to load
        self.config_tree.bind('<Double-1>', self._on_config_double_click)
        
        # Config buttons
        config_btn_frame = ttk.Frame(config_frame)
        config_btn_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Button(config_btn_frame, text="💾 Save", command=self._quick_save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="💾 Save As...", command=self._show_save_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="📂 Load Selected", command=self._load_selected_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="🗑️ Delete Selected", command=self._delete_selected_config).pack(side=tk.LEFT)
        ttk.Button(config_btn_frame, text="🔄 Refresh", command=self._refresh_config_list).pack(side=tk.RIGHT)
        
        # ===== Control Section =====
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Start/Stop buttons - make them prominent
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(btn_frame, text="▶  START  (F7)", command=self._start_autoclicker,
                                   bg='#28a745', fg='white', font=('Arial', 11, 'bold'),
                                   activebackground='#218838', activeforeground='white',
                                   width=15, height=2, cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(btn_frame, text="⏹  STOP  (F8)", command=self._stop_autoclicker,
                                  bg='#dc3545', fg='white', font=('Arial', 11, 'bold'),
                                  activebackground='#c82333', activeforeground='white',
                                  width=15, height=2, state='disabled', cursor='hand2')
        self.stop_btn.pack(side=tk.LEFT)
        
        # ===== Status Section =====
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready - Press F6 to add click points", 
                                     font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.stats_label = ttk.Label(status_frame, text="Loops: 0 | Clicks: 0", 
                                    font=('Arial', 9), foreground='gray')
        self.stats_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def _on_rapid_add_mode(self, start_mode=False):
        """Enter rapid add mode - F6 was pressed"""
        self.rapid_add_active = True
        self._on_status_change("RAPID ADD MODE: Move mouse, press 0-9 for delay (0=10s), F6 again for default (3s), F9/ESC to exit")
    
    def _on_number_key(self, delay):
        """Handle number key press in rapid add mode - add point with specified delay"""
        if not self.rapid_add_active:
            return
        
        x, y = self.mouse.position
        
        # Create and add the point with the specified delay
        point = ClickPoint(
            x=x, y=y,
            delay=float(delay),
            randomize=False,
            random_range=0
        )
        self.autoclicker.add_point(point)
        self._refresh_tree()
        self._on_status_change(f"Added point at ({x}, {y}) with {delay}s delay - Next: move mouse + number, or F9/ESC to exit")
    
    def _on_exit_rapid_add(self):
        """Exit rapid add mode"""
        self.rapid_add_active = False
        self._on_status_change("Rapid add mode exited - Press F6 to add more, F7 to start")
    
    def _capture_cursor(self):
        """Legacy method - capture current cursor position and add as click point immediately"""
        x, y = self.mouse.position
        
        # Create and add the point immediately with default values
        point = ClickPoint(
            x=x, y=y,
            delay=3.0,  # Default delay
            randomize=False,
            random_range=0
        )
        self.autoclicker.add_point(point)
        self._refresh_tree()
        self._on_status_change(f"Added click point at ({x}, {y}) - Double-click or press Enter to edit")
        
    def _refresh_tree(self):
        """Refresh the treeview with current click points"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add points
        for i, point in enumerate(self.autoclicker.click_points, 1):
            self.tree.insert('', tk.END, values=(
                i,
                point.x,
                point.y,
                f"{point.delay:.1f}",
                "Yes" if point.randomize else "No",
                point.random_range if point.randomize else "-",
                "✓" if point.enabled else "✗"
            ))
            
    def _remove_selected(self):
        """Remove selected click point"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a click point to remove")
            return
        
        index = self.tree.index(selection[0])
        self.autoclicker.remove_point(index)
        self._refresh_tree()
        
    def _clear_all(self):
        """Clear all click points"""
        if not self.autoclicker.click_points:
            return
        if messagebox.askyesno("Confirm", "Clear all click points?"):
            self.autoclicker.clear_points()
            self._refresh_tree()
            
    def _on_tree_double_click(self, event):
        """Edit click point on double click"""
        selection = self.tree.selection()
        if not selection:
            return
            
        index = self.tree.index(selection[0])
        point = self.autoclicker.click_points[index]
        
        # Edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Click Point")
        dialog.geometry("300x280")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # X, Y
        ttk.Label(frame, text="X:").grid(row=0, column=0, sticky=tk.W)
        x_var = tk.IntVar(value=point.x)
        x_spinbox = ttk.Spinbox(frame, from_=0, to=9999, textvariable=x_var, width=10)
        x_spinbox.grid(row=0, column=1, sticky=tk.W, pady=2)
        x_spinbox.focus()
        
        ttk.Label(frame, text="Y:").grid(row=1, column=0, sticky=tk.W)
        y_var = tk.IntVar(value=point.y)
        ttk.Spinbox(frame, from_=0, to=9999, textvariable=y_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Delay
        ttk.Label(frame, text="Delay (s):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        delay_var = tk.DoubleVar(value=point.delay)
        ttk.Spinbox(frame, from_=0.1, to=300.0, increment=0.1, textvariable=delay_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Randomize
        randomize_var = tk.BooleanVar(value=point.randomize)
        ttk.Checkbutton(frame, text="Randomize", variable=randomize_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Range
        ttk.Label(frame, text="Random range:").grid(row=4, column=0, sticky=tk.W)
        range_var = tk.IntVar(value=point.random_range)
        ttk.Spinbox(frame, from_=1, to=100, textvariable=range_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Enabled
        enabled_var = tk.BooleanVar(value=point.enabled)
        ttk.Checkbutton(frame, text="Enabled", variable=enabled_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        def save_changes():
            point.x = x_var.get()
            point.y = y_var.get()
            point.delay = delay_var.get()
            point.randomize = randomize_var.get()
            point.random_range = range_var.get()
            point.enabled = enabled_var.get()
            self._refresh_tree()
            dialog.destroy()
            
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
    def _start_autoclicker(self):
        """Start the autoclicker"""
        if not self.autoclicker.click_points:
            messagebox.showinfo("Info", "Please add at least one click point first (Press F6)")
            return
            
        self.autoclicker.start_delay = self.start_delay_var.get()
        self.autoclicker.loop_count = self.loop_count_var.get()
        self.autoclicker.verify_position = self.verify_pos_var.get()
        self.autoclicker.debug_mode = self.debug_mode_var.get()
        
        if self.autoclicker.start():
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
            
    def _stop_autoclicker(self):
        """Stop the autoclicker"""
        self.autoclicker.stop()
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        
    def _get_config_files(self):
        """Get list of config files in the configs directory"""
        configs_dir = get_configs_dir()
        if not os.path.exists(configs_dir):
            return []
        return [f for f in os.listdir(configs_dir) if f.endswith('.json')]
        
    def _on_status_change(self, status):
        """Handle status updates"""
        self.root.after(0, lambda: self.status_label.configure(text=status))
        
    def _on_click(self, point_index, position, total_clicks):
        """Handle click event"""
        self.root.after(0, lambda: self.stats_label.configure(
            text=f"Loops: {self.autoclicker.current_loop} | Clicks: {total_clicks}"
        ))
        
    def _schedule_updates(self):
        """Schedule periodic UI updates"""
        self._update_ui()
        self.root.after(100, self._schedule_updates)
        
    def _update_ui(self):
        """Update UI elements"""
        if self.autoclicker.running:
            # Update buttons
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
        else:
            self.start_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')
            
        # Update stats
        self.stats_label.configure(
            text=f"Loops: {self.autoclicker.current_loop} | Clicks: {self.autoclicker.click_count}"
        )
        
    def _refresh_config_list(self):
        """Refresh the list of saved configurations"""
        # Clear existing
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)
        
        configs_dir = get_configs_dir()
        if not os.path.exists(configs_dir):
            return
        
        # Load each config file and add to tree
        for filename in sorted(os.listdir(configs_dir)):
            if filename.endswith('.json'):
                filepath = os.path.join(configs_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        config = json.load(f)
                    
                    name = config.get('name', filename)
                    description = config.get('description', '')
                    points = len(config.get('click_points', []))
                    saved_at = config.get('saved_at', 'Unknown')
                    # Format date for display
                    if saved_at != 'Unknown':
                        try:
                            dt = datetime.fromisoformat(saved_at)
                            saved_at = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            pass
                    
                    self.config_tree.insert('', tk.END, values=(name, description, points, saved_at), tags=(filepath,))
                except:
                    pass  # Skip invalid config files
    
    def _show_save_dialog(self):
        """Show dialog to save current config with name and description"""
        if not self.autoclicker.click_points:
            messagebox.showinfo("Info", "No click points to save")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Configuration")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Config name
        ttk.Label(frame, text="Configuration Name:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        name_var = tk.StringVar(value=f"Config {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        name_entry = ttk.Entry(frame, textvariable=name_var, width=40)
        name_entry.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Description
        ttk.Label(frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(frame, textvariable=desc_var, width=40)
        desc_entry.pack(anchor=tk.W, fill=tk.X, pady=(0, 5))
        ttk.Label(frame, text="e.g., 'Fishing at Barbarian Village' or 'Woodcutting at Draynor'", 
                 foreground='gray', font=('Arial', 8)).pack(anchor=tk.W)
        
        def do_save():
            name = name_var.get().strip()
            description = desc_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a configuration name")
                return
            
            # Create safe filename from name
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            if not safe_name:
                safe_name = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            configs_dir = get_configs_dir()
            filepath = os.path.join(configs_dir, f"{safe_name}.json")
            
            # Handle duplicate names
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(configs_dir, f"{safe_name}_{counter}.json")
                counter += 1
            
            try:
                self.autoclicker.save_config(filepath, name, description)
                self._refresh_config_list()
                dialog.destroy()
                messagebox.showinfo("Success", f"Configuration '{name}' saved!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(20, 0))
        ttk.Button(btn_frame, text="Save", command=do_save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Bind Enter to save
        dialog.bind('<Return>', lambda e: do_save())
        
        # Center dialog
        dialog.update_idletasks()
        dialog.geometry(f"+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")
    
    def _on_config_double_click(self, event):
        """Load config on double click"""
        self._load_selected_config()
    
    def _load_selected_config(self):
        """Load the selected configuration"""
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a configuration to load")
            return
        
        filepath = self.config_tree.item(selection[0], 'tags')[0]
        
        try:
            config = self.autoclicker.load_config(filepath)
            self.start_delay_var.set(self.autoclicker.start_delay)
            self.loop_count_var.set(self.autoclicker.loop_count)
            self._refresh_tree()
            name = config.get('name', 'Unnamed')
            # Track loaded config for quick save
            self.current_config_path = filepath
            self.current_config_name = name
            self._update_status_with_config()
            messagebox.showinfo("Success", f"Configuration '{name}' loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def _update_status_with_config(self):
        """Update status label to show currently loaded config"""
        if self.current_config_name:
            self.status_label.configure(text=f"Loaded: {self.current_config_name} - Press F6 to add click points")
        else:
            self.status_label.configure(text="Ready - Press F6 to add click points")
    
    def _quick_save_config(self):
        """Quick save to update the currently loaded config"""
        if not self.autoclicker.click_points:
            messagebox.showinfo("Info", "No click points to save")
            return
        
        if not self.current_config_path:
            # No config loaded, use Save As instead
            self._show_save_dialog()
            return
        
        # Load existing config to preserve name and description
        try:
            with open(self.current_config_path, 'r') as f:
                existing_config = json.load(f)
            name = existing_config.get('name', self.current_config_name or 'Unnamed')
            description = existing_config.get('description', '')
        except:
            name = self.current_config_name or 'Unnamed'
            description = ''
        
        try:
            self.autoclicker.save_config(self.current_config_path, name, description)
            self._refresh_config_list()
            messagebox.showinfo("Success", f"Configuration '{name}' updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def _delete_selected_config(self):
        """Delete the selected configuration"""
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a configuration to delete")
            return
        
        filepath = self.config_tree.item(selection[0], 'tags')[0]
        name = self.config_tree.item(selection[0], 'values')[0]
        
        if messagebox.askyesno("Confirm", f"Delete configuration '{name}'?"):
            try:
                os.remove(filepath)
                self._refresh_config_list()
                messagebox.showinfo("Success", f"Configuration '{name}' deleted!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
                
    def run(self):
        """Start the GUI main loop"""
        try:
            self.root.mainloop()
        finally:
            self.hotkey_listener.stop()
            self.autoclicker.stop()


def main():
    """Main entry point"""
    print("=" * 50)
    print("OSRS AutoClicker")
    print("=" * 50)
    print("Hotkeys:")
    print("  F6     - Enter Rapid Add Mode")
    print("  0-9    - Set delay in seconds (0 = 10s)")
    print("  F9/ESC - Exit Rapid Add Mode")
    print("  F7     - Start autoclicker")
    print("  F8     - Stop autoclicker")
    print("=" * 50)
    print("Rapid Add Mode: F6 → move mouse → press number → repeat → F9")
    print("=" * 50)
    
    app = AutoClickerGUI()
    app.run()


if __name__ == "__main__":
    main()
