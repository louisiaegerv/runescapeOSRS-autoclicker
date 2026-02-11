"""
Dialog classes for the autoclicker GUI.

Contains dialog windows for editing click points and saving configurations.
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from ..utils import get_configs_dir


class EditPointDialog:
    """Dialog for editing a click point"""
    
    def __init__(self, parent, point, on_save_callback):
        """
        Initialize the edit dialog.
        
        Args:
            parent: Parent tkinter widget
            point: ClickPoint object to edit
            on_save_callback: Function to call when saving changes
        """
        self.point = point
        self.on_save = on_save_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Click Point")
        self.dialog.geometry("300x280")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._build_form()
        
    def _build_form(self):
        """Build the form fields"""
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # X, Y
        ttk.Label(frame, text="X:").grid(row=0, column=0, sticky=tk.W)
        self.x_var = tk.IntVar(value=self.point.x)
        x_spinbox = ttk.Spinbox(frame, from_=0, to=9999, textvariable=self.x_var, width=10)
        x_spinbox.grid(row=0, column=1, sticky=tk.W, pady=2)
        x_spinbox.focus()
        
        ttk.Label(frame, text="Y:").grid(row=1, column=0, sticky=tk.W)
        self.y_var = tk.IntVar(value=self.point.y)
        ttk.Spinbox(frame, from_=0, to=9999, textvariable=self.y_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Delay
        ttk.Label(frame, text="Delay (s):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.delay_var = tk.DoubleVar(value=self.point.delay)
        ttk.Spinbox(frame, from_=0.1, to=300.0, increment=0.1, textvariable=self.delay_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Randomize
        self.randomize_var = tk.BooleanVar(value=self.point.randomize)
        ttk.Checkbutton(frame, text="Randomize", variable=self.randomize_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Range
        ttk.Label(frame, text="Random range:").grid(row=4, column=0, sticky=tk.W)
        self.range_var = tk.IntVar(value=self.point.random_range)
        ttk.Spinbox(frame, from_=1, to=100, textvariable=self.range_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Enabled
        self.enabled_var = tk.BooleanVar(value=self.point.enabled)
        ttk.Checkbutton(frame, text="Enabled", variable=self.enabled_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
    def _save(self):
        """Save changes and close dialog"""
        self.point.x = self.x_var.get()
        self.point.y = self.y_var.get()
        self.point.delay = self.delay_var.get()
        self.point.randomize = self.randomize_var.get()
        self.point.random_range = self.range_var.get()
        self.point.enabled = self.enabled_var.get()
        self.on_save()
        self.dialog.destroy()


class SaveConfigDialog:
    """Dialog for saving a configuration"""
    
    def __init__(self, parent, autoclicker, on_save_callback):
        """
        Initialize the save dialog.
        
        Args:
            parent: Parent tkinter widget
            autoclicker: AutoClicker instance
            on_save_callback: Function to call after saving (receives name, filepath)
        """
        self.autoclicker = autoclicker
        self.on_save = on_save_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Save Configuration")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._build_form()
        
    def _build_form(self):
        """Build the form fields"""
        frame = ttk.Frame(self.dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Config name
        ttk.Label(frame, text="Configuration Name:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=f"Config {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        name_entry = ttk.Entry(frame, textvariable=self.name_var, width=40)
        name_entry.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Description
        ttk.Label(frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(frame, textvariable=self.desc_var, width=40)
        desc_entry.pack(anchor=tk.W, fill=tk.X, pady=(0, 5))
        ttk.Label(frame, text="e.g., 'Fishing at Barbarian Village' or 'Woodcutting at Draynor'", 
                 foreground='gray', font=('Arial', 8)).pack(anchor=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(20, 0))
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        # Bind Enter to save
        self.dialog.bind('<Return>', lambda e: self._save())
        
        # Center dialog
        self.dialog.update_idletasks()
        parent_x = self.dialog.master.winfo_x()
        parent_y = self.dialog.master.winfo_y()
        self.dialog.geometry(f"+{parent_x + 100}+{parent_y + 100}")
        
    def _save(self):
        """Save the configuration"""
        name = self.name_var.get().strip()
        description = self.desc_var.get().strip()
        
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
            self.on_save()
            self.dialog.destroy()
            messagebox.showinfo("Success", f"Configuration '{name}' saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
