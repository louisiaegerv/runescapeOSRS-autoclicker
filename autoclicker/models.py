"""
Data models for the autoclicker package.

This module contains the ClickPoint class which represents a single
click location with its associated settings.
"""

import random


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
        """Convert ClickPoint to dictionary for serialization."""
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
        """Create ClickPoint from dictionary."""
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
