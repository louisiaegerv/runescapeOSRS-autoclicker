"""
UI section builder module.

Contains classes for building different sections of the main window.
"""

import tkinter as tk
from tkinter import ttk


class HeaderSection:
    """Header section showing hotkey information"""
    
    @staticmethod
    def build(parent):
        """
        Build the header section.
        
        Args:
            parent: Parent frame to build in
            
        Returns:
            The created header frame
        """
        header_frame = ttk.LabelFrame(parent, text="Hotkeys", padding="10")
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
        
        return header_frame


class SettingsSection:
    """Settings section with configuration options"""
    
    def __init__(self):
        self.start_delay_var = None
        self.loop_count_var = None
        self.verify_pos_var = None
        self.debug_mode_var = None
        
    def build(self, parent):
        """
        Build the settings section.
        
        Args:
            parent: Parent frame to build in
            
        Returns:
            The created settings frame
        """
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding="10")
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
        
        return settings_frame


class ControlsSection:
    """Controls section with start/stop buttons"""
    
    def __init__(self):
        self.start_btn = None
        self.stop_btn = None
        
    def build(self, parent, on_start, on_stop):
        """
        Build the controls section.
        
        Args:
            parent: Parent frame to build in
            on_start: Callback for start button
            on_stop: Callback for stop button
            
        Returns:
            The created controls frame
        """
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Start/Stop buttons - make them prominent
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(btn_frame, text="▶  START  (F7)", command=on_start,
                                   bg='#28a745', fg='white', font=('Arial', 11, 'bold'),
                                   activebackground='#218838', activeforeground='white',
                                   width=15, height=2, cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(btn_frame, text="⏹  STOP  (F8)", command=on_stop,
                                  bg='#dc3545', fg='white', font=('Arial', 11, 'bold'),
                                  activebackground='#c82333', activeforeground='white',
                                  width=15, height=2, state='disabled', cursor='hand2')
        self.stop_btn.pack(side=tk.LEFT)
        
        return control_frame
        
    def set_running(self, running):
        """Update button states based on running status"""
        if running:
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
        else:
            self.start_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')


class StatusSection:
    """Status section showing current status and statistics"""
    
    def __init__(self):
        self.status_label = None
        self.stats_label = None
        self.progress_var = None
        self.progress_bar = None
        
    def build(self, parent):
        """
        Build the status section.
        
        Args:
            parent: Parent frame to build in
            
        Returns:
            The created status frame
        """
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
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
        
        return status_frame
        
    def update_status(self, text):
        """Update the status label text"""
        self.status_label.configure(text=text)
        
    def update_stats(self, loops, clicks):
        """Update the stats label"""
        self.stats_label.configure(text=f"Loops: {loops} | Clicks: {clicks}")
