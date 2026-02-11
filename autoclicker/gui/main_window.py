"""
Main window module for the autoclicker GUI.

Contains the AutoClickerGUI class which coordinates all UI components.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from pynput.mouse import Controller as MouseController

from ..core import AutoClicker
from ..hotkeys import HotkeyListener
from ..models import ClickPoint
from .config_panel import ConfigPanel
from .dialogs import SaveConfigDialog
from .points_panel import PointsPanel
from .sections import ControlsSection, HeaderSection, SettingsSection, StatusSection


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
        
        # Build GUI
        self._build_gui()
        
        # Start hotkey listener
        self.hotkey_listener.start()
        
        # Update loop for status
        self._schedule_updates()
        
    def _build_gui(self):
        """Build the GUI components with scrollable container"""
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create main container frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create canvas with scrollbar
        self.canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, padding="10")

        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Create window inside canvas for the scrollable frame
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure scrollable frame grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(2, weight=1)  # Click points list row
        self.scrollable_frame.rowconfigure(3, weight=1)  # Config list row

        # Bind events for scrolling
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse wheel for scrolling
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.scrollable_frame)

        # Build sections inside scrollable frame
        HeaderSection.build(self.scrollable_frame)

        self.settings = SettingsSection()
        self.settings.build(self.scrollable_frame)

        self.points_panel = PointsPanel(self.scrollable_frame, self.autoclicker, self._on_status_change)

        self.config_panel = ConfigPanel(self.scrollable_frame, self.autoclicker, self._on_config_action)
        self.config_panel.refresh()  # Load saved configs list

        self.controls = ControlsSection()
        self.controls.build(self.scrollable_frame, self._start_autoclicker, self._stop_autoclicker)

        self.status = StatusSection()
        self.status.build(self.scrollable_frame)

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """When canvas is resized, resize the inner frame width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _bind_mousewheel(self, widget):
        """Bind mouse wheel events to the widget for scrolling"""
        def _on_mousewheel(event):
            # Handle different event types for different platforms
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")

        # Windows and macOS
        widget.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        # Linux
        widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        # Also bind to children widgets recursively
        for child in widget.winfo_children():
            self._bind_mousewheel(child)
        
    def _on_config_action(self, config_data):
        """Handle config panel actions"""
        if config_data.get('__action__') == 'show_save_dialog':
            self._show_save_dialog()
        else:
            # Config was loaded - update settings
            self.settings.start_delay_var.set(self.autoclicker.start_delay)
            self.settings.loop_count_var.set(self.autoclicker.loop_count)
            self.points_panel.refresh()
            self._update_status_with_config(config_data.get('name'))
            
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
        self.points_panel.refresh()
        self._on_status_change(f"Added point at ({x}, {y}) with {delay}s delay - Next: move mouse + number, or F9/ESC to exit")
    
    def _on_exit_rapid_add(self):
        """Exit rapid add mode"""
        self.rapid_add_active = False
        self._on_status_change("Rapid add mode exited - Press F6 to add more, F7 to start")
        
    def _start_autoclicker(self):
        """Start the autoclicker"""
        if not self.autoclicker.click_points:
            messagebox.showinfo("Info", "Please add at least one click point first (Press F6)")
            return
            
        self.autoclicker.start_delay = self.settings.start_delay_var.get()
        self.autoclicker.loop_count = self.settings.loop_count_var.get()
        self.autoclicker.verify_position = self.settings.verify_pos_var.get()
        self.autoclicker.debug_mode = self.settings.debug_mode_var.get()
        
        if self.autoclicker.start():
            self.controls.set_running(True)
            
    def _stop_autoclicker(self):
        """Stop the autoclicker"""
        self.autoclicker.stop()
        self.controls.set_running(False)
        
    def _on_status_change(self, status):
        """Handle status updates"""
        self.root.after(0, lambda: self.status.update_status(status))
        
    def _on_click(self, point_index, position, total_clicks):
        """Handle click event"""
        self.root.after(0, lambda: self.status.update_stats(
            self.autoclicker.current_loop, total_clicks
        ))
        
    def _schedule_updates(self):
        """Schedule periodic UI updates"""
        self._update_ui()
        self.root.after(100, self._schedule_updates)
        
    def _update_ui(self):
        """Update UI elements"""
        self.controls.set_running(self.autoclicker.running)
        self.status.update_stats(self.autoclicker.current_loop, self.autoclicker.click_count)
        
    def _show_save_dialog(self):
        """Show dialog to save current config with name and description"""
        if not self.autoclicker.click_points:
            messagebox.showinfo("Info", "No click points to save")
            return
        
        def on_save_complete():
            self.config_panel.refresh()
            
        SaveConfigDialog(self.root, self.autoclicker, on_save_complete)
    
    def _update_status_with_config(self, config_name):
        """Update status label to show currently loaded config"""
        if config_name:
            self.status.update_status(f"Loaded: {config_name} - Press F6 to add click points")
        else:
            self.status.update_status("Ready - Press F6 to add click points")
            
    def run(self):
        """Start the GUI main loop"""
        try:
            self.root.mainloop()
        finally:
            self.hotkey_listener.stop()
            self.autoclicker.stop()
