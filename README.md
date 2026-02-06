# OSRS AutoClicker

A feature-rich autoclicker designed for AFK skilling in Old School RuneScape (OSRS) on self-hosted private servers.

## Features

- **Multiple Click Points**: Add as many click locations as you need, each with its own delay
- **Rapid Add Mode**: Press F6 to enter rapid add mode, then press 0-9 to capture cursor positions with preset delays
- **Configurable Delays**: Set individual delays for each click point
- **Position Randomization**: Add randomness to click positions to appear more human-like
- **Save/Load Configurations**: Save your click patterns for different skilling activities with names and descriptions
- **Visual Feedback**: Real-time status updates, statistics, and progress bar
- **Loop Control**: Set a specific number of loops or run infinitely
- **Start Delay**: Grace period before clicking begins (time to switch to game window)
- **Debug Mode**: Optional console output showing actual click coordinates
- **Position Verification**: Prevents mouse drift by re-checking position before clicking

## Hotkeys

| Key | Action |
|-----|--------|
| **F6** | Enter Rapid Add Mode (capture cursor position) |
| **0-9** | Set delay in seconds while in Rapid Add Mode (0 = 10 seconds) |
| **F9 / ESC** | Exit Rapid Add Mode |
| **F7** | Start the autoclicker |
| **F8** | Stop the autoclicker |

## Installation

1. Install Python 3.8 or higher
2. Install the required dependency:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

1. Run the script:
   ```bash
   python autoclicker.py
   ```

2. **Set up click points using Rapid Add Mode**:
   - Press **F6** to enter Rapid Add Mode
   - Move your mouse to the desired click location
   - Press **0-9** to set the delay (in seconds) for that point
   - Repeat for each click point
   - Press **F9** or **ESC** to exit Rapid Add Mode

3. **Configure settings**:
   - Set "Start Delay" - time before the first click (to switch to game window)
   - Set "Loop Count" - number of times to repeat the sequence (0 = infinite)
   - Enable "Verify click position" to prevent mouse drift

4. **Start clicking**:
   - Press **F7** or click the START button
   - The status will show the countdown and then loop progress

5. **Stop anytime**:
   - Press **F8** or click the STOP button

### Editing Click Points

- **Double-click** any point in the list to edit its coordinates, delay, or randomization settings
- Use the "Remove Selected" button to delete a point
- Use the "Clear All" button to remove all points

### Saving Configurations

1. Set up your click points for a specific activity (e.g., fishing, woodcutting, mining)
2. Click "💾 Save" to quick-save an existing config, or "💾 Save As..." for a new config
3. Enter a name and optional description
4. Configs are saved to the `configs/` directory

### Loading Configurations

1. Select a configuration from the "Saved Configurations" list
2. Click "📂 Load Selected" or double-click the config
3. Your click points and settings will be restored

### Deleting Configurations

- Select a configuration and click "🗑️ Delete Selected" to remove it

## Configuration File Format

Configurations are saved as JSON files in the `configs/` directory:

```json
{
  "name": "Fishing Config",
  "description": "3-tick fishing at Barbarian Village",
  "start_delay": 3.0,
  "loop_count": 0,
  "click_points": [
    {
      "x": 500,
      "y": 400,
      "delay": 1.5,
      "randomize": true,
      "random_range": 8,
      "enabled": true
    }
  ],
  "saved_at": "2026-02-06T10:00:00"
}
```

## Example Configurations

### 3-Tick Fishing
```
Point 1: (x, y) - Drop fish 1, delay 0.6s
Point 2: (x, y) - Drop fish 2, delay 0.6s  
Point 3: (x, y) - Click fishing spot, delay 1.8s
Loop: Infinite
```

### AFK Woodcutting
```
Point 1: (x, y) - Click tree, delay 25s (wait for full inventory)
Point 2: (x, y) - Click drop item, delay 0.1s
Point 3: (x, y) - Click drop item, delay 0.1s
... (repeat for inventory)
Loop: Infinite
```

### Simple Banking
```
Point 1: (x, y) - Click bank booth, delay 2s
Point 2: (x, y) - Click "Bank All", delay 1s
Point 3: (x, y) - Close bank, delay 1s
Loop: Set to desired number
```

## Tips

1. **Test First**: Always test with a short loop count before running for extended periods
2. **Randomization**: Enable position randomization (5-15 pixels) for longer sessions
3. **Start Delay**: Use at least 3 seconds to switch to your game window
4. **Backup Configs**: Save configurations with descriptive names like "barbarian_fishing.json"
5. **Window Position**: Keep your game window in the same position when using saved configs
6. **Rapid Add Mode**: This is the fastest way to set up multiple click points
7. **Debug Mode**: Enable this in settings to see actual click coordinates in the console

## Safety Notes

- This tool is intended for **self-hosted private servers only**
- Using autoclickers on official OSRS servers is against the rules and can result in bans
- Always verify you're on your private server before running

## Troubleshooting

**"Failed to save/load" errors**: Ensure you have write permissions in the script directory

**Hotkeys not working**: Make sure the script is focused or try running as administrator

**Clicks not registering**: Increase the delay after each click to ensure the game registers it

**Mouse position drift**: Enable "Verify click position" in settings to ensure clicks happen at the intended location

## Requirements

- Python 3.8+
- pynput >= 1.7.6

## License

Use at your own risk. For educational and private server use only.
