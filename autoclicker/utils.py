"""
Utility functions and constants for the autoclicker package.
"""

import os

# Default configs directory
CONFIGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "configs")


def get_configs_dir():
    """Get or create the configs directory"""
    if not os.path.exists(CONFIGS_DIR):
        os.makedirs(CONFIGS_DIR)
    return CONFIGS_DIR
