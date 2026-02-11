"""
Entry point for the OSRS AutoClicker application.

This module provides the main entry point to run the autoclicker GUI.
It can be run directly or imported as a module.
"""

from .gui import AutoClickerGUI


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
    print("Rapid Add Mode: F6 -> move mouse -> press number -> repeat -> F9")
    print("=" * 50)
    
    app = AutoClickerGUI()
    app.run()


if __name__ == "__main__":
    main()
