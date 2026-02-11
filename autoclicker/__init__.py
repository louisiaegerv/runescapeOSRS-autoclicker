"""
OSRS AutoClicker - A feature-rich autoclicker for AFK skilling

This package provides a modular autoclicker with:
- Multiple click locations with individual delays
- Hotkey-based coordinate capture
- Save/load click configurations
- Randomization options for anti-detection
"""

from .models import ClickPoint
from .core import AutoClicker
from .hotkeys import HotkeyListener
from .gui import AutoClickerGUI
from .utils import get_configs_dir, CONFIGS_DIR

__all__ = [
    'ClickPoint',
    'AutoClicker',
    'HotkeyListener',
    'AutoClickerGUI',
    'get_configs_dir',
    'CONFIGS_DIR',
]

__version__ = '1.0.0'
