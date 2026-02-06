# OSRS AutoClicker

A feature-rich autoclicker designed for AFK skilling in Old School RuneScape (OSRS) on self-hosted private servers.

## Features

- **Multiple Click Points**: Add as many click locations as you need, each with its own delay
- **Hotkey Capture**: Press F6 to instantly capture your cursor position - no manual coordinate entry
- **Configurable Delays**: Set individual delays for each click point
- **Position Randomization**: Add randomness to click positions to appear more human-like
- **Save/Load Configurations**: Save your click patterns for different skilling activities
- **Visual Feedback**: Real-time status updates and statistics
- **Loop Control**: Set a specific number of loops or run infinitely
- **Start Delay**: Grace period before clicking begins (time to switch to game window)

## Hotkeys

| Key | Action |
|-----|--------|
| **F6** | Capture cursor position and add as click point |
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
   python osrs_autoclicker.py
   ```

2. **Set up click points**:
   - Position your cursor where you want to click in-game
   - Press **F6** to capture that position
   - Set the delay (time to wait AFTER this click before the next one)
   - Optionally enable randomization for more natural clicks
   - Click "Add"

3. **Configure settings**:
   - Set "Start Delay" - time before the first click (to switch to game window)
   - Set "Loop Count" - number of times to repeat the sequence (0 = infinite)

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
2. Click "💾 Save Config"
3. Choose a filename (defaults include timestamp)

### Loading Configurations

1. Click "📂 Load Config"
2. Select your saved JSON file
3. Your click points and settings will be restored

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

## Safety Notes

- This tool is intended for **self-hosted private servers only**
- Using autoclickers on official OSRS servers is against the rules and can result in bans
- Always verify you're on your private server before running

## Troubleshooting

**"Failed to save/load" errors**: Ensure you have write permissions in the script directory

**Hotkeys not working**: Make sure the script is focused or try running as administrator

**Clicks not registering**: Increase the delay after each click to ensure the game registers it

## License

Use at your own risk. For educational and private server use only.
