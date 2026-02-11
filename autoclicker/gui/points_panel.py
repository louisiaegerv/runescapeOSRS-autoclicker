"""
Click points panel module.

Contains the PointsPanel class for managing click points treeview and actions.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from ..models import ClickPoint
from .dialogs import EditPointDialog


class PointsPanel:
    """Panel for managing click points"""
    
    def __init__(self, parent, autoclicker, on_status_change):
        """
        Initialize the points panel.
        
        Args:
            parent: Parent tkinter widget (frame)
            autoclicker: AutoClicker instance
            on_status_change: Callback for status updates
        """
        self.autoclicker = autoclicker
        self.on_status_change = on_status_change
        self.tree = None
        
        self._build_panel(parent)
        
    def _build_panel(self, parent):
        """Build the panel UI"""
        # Points frame
        points_frame = ttk.LabelFrame(parent, text="Click Points", padding="10")
        points_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        points_frame.columnconfigure(0, weight=1)
        
        # Buttons row
        btn_frame = ttk.Frame(points_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(btn_frame, text="➕ Add Point (F6)", command=self._show_add_message).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📋 Clear All", command=self.clear_all).pack(side=tk.LEFT)
        
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
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Return>', self._on_double_click)
        
    def _show_add_message(self):
        """Show message about how to add points"""
        messagebox.showinfo("Add Point", "Press F6 to enter Rapid Add Mode, then move your mouse and press 0-9 to set the delay.")
        
    def refresh(self):
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
            
    def remove_selected(self):
        """Remove selected click point"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a click point to remove")
            return
        
        index = self.tree.index(selection[0])
        self.autoclicker.remove_point(index)
        self.refresh()
        
    def clear_all(self):
        """Clear all click points"""
        if not self.autoclicker.click_points:
            return
        if messagebox.askyesno("Confirm", "Clear all click points?"):
            self.autoclicker.clear_points()
            self.refresh()
            
    def _on_double_click(self, event=None):
        """Edit click point on double click"""
        selection = self.tree.selection()
        if not selection:
            return
            
        index = self.tree.index(selection[0])
        point = self.autoclicker.click_points[index]
        
        EditPointDialog(self.tree.winfo_toplevel(), point, self.refresh)
        
    def get_selection(self):
        """Get current treeview selection"""
        return self.tree.selection()
        
    def select_item(self, item_id):
        """Select a specific item in the treeview"""
        self.tree.selection_set(item_id)
        self.tree.see(item_id)
