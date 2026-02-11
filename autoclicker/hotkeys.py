"""
Global hotkey listener module.

This module contains the HotkeyListener class which handles global
hotkey events using pynput for features like rapid add mode and
start/stop controls.
"""

from pynput.keyboard import Listener, Key, KeyCode


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
