"""
Configuration panel module.

Contains the ConfigPanel class for managing saved configurations.
"""

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from ..utils import get_configs_dir


class ConfigPanel:
    """Panel for managing saved configurations"""
    
    def __init__(self, parent, autoclicker, on_config_loaded):
        """
        Initialize the config panel.
        
        Args:
            parent: Parent tkinter widget (frame)
            autoclicker: AutoClicker instance
            on_config_loaded: Callback when config is loaded (receives config dict)
        """
        self.autoclicker = autoclicker
        self.on_config_loaded = on_config_loaded
        self.config_tree = None
        self.current_config_path = None
        self.current_config_name = None
        
        self._build_panel(parent)
        
    def _build_panel(self, parent):
        """Build the panel UI"""
        # Config frame
        config_frame = ttk.LabelFrame(parent, text="Saved Configurations", padding="10")
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
        self.config_tree.bind('<Double-1>', self._on_double_click)
        
        # Config buttons
        config_btn_frame = ttk.Frame(config_frame)
        config_btn_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Button(config_btn_frame, text="💾 Save", command=self.quick_save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="💾 Save As...", command=self._show_save_dialog_callback).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="📂 Load Selected", command=self.load_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="🗑️ Delete Selected", command=self.delete_selected).pack(side=tk.LEFT)
        ttk.Button(config_btn_frame, text="🔄 Refresh", command=self.refresh).pack(side=tk.RIGHT)
        
    def _show_save_dialog_callback(self):
        """Trigger the save dialog callback"""
        if self.on_config_loaded:
            # Use a special flag to indicate save dialog should be shown
            self.on_config_loaded({'__action__': 'show_save_dialog'})
            
    def _on_double_click(self, event=None):
        """Load config on double click"""
        self.load_selected()
        
    def refresh(self):
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
                    
    def load_selected(self):
        """Load the selected configuration"""
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a configuration to load")
            return
        
        filepath = self.config_tree.item(selection[0], 'tags')[0]
        
        try:
            config = self.autoclicker.load_config(filepath)
            # Track loaded config for quick save
            self.current_config_path = filepath
            self.current_config_name = config.get('name', 'Unnamed')
            
            # Notify parent
            if self.on_config_loaded:
                self.on_config_loaded(config)
                
            messagebox.showinfo("Success", f"Configuration '{self.current_config_name}' loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")
            
    def quick_save(self):
        """Quick save to update the currently loaded config"""
        if not self.autoclicker.click_points:
            messagebox.showinfo("Info", "No click points to save")
            return
        
        if not self.current_config_path:
            # No config loaded, trigger save as
            if self.on_config_loaded:
                self.on_config_loaded({'__action__': 'show_save_dialog'})
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
            self.refresh()
            messagebox.showinfo("Success", f"Configuration '{name}' updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
            
    def delete_selected(self):
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
                self.refresh()
                messagebox.showinfo("Success", f"Configuration '{name}' deleted!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
                
    def get_current_config_info(self):
        """Get current config path and name for external reference"""
        return self.current_config_path, self.current_config_name
        
    def set_current_config(self, path, name):
        """Set current config info"""
        self.current_config_path = path
        self.current_config_name = name
