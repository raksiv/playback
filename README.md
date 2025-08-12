# Mouse Automation Suite

A collection of tools for mouse and keyboard automation on macOS, including location learning, script recording/playback, and human-readable automation scripts.

## Project Structure

```
/
├── bin/                    # Executable wrapper scripts
│   ├── play               # Quick access to script execution
│   ├── record             # Record automation sessions
│   ├── playback           # Playback recorded sessions
│   └── remap              # Remap recordings for different machines
├── src/
│   ├── core/              # Main functionality
│   │   ├── simon_says.py  # Execute human-readable automation scripts
│   │   └── script_recorder.py # Record automation sessions
│   └── tools/             # Utilities and helpers
│       ├── position.py    # Position utilities
│       └── main.py        # Additional tools
├── recordings/            # Recorded automation sessions
│   └── rec1/              # Example recording
│       ├── script.txt     # Automation commands
│       ├── locations.json # Session-specific locations
│       └── info.json      # Recording metadata
├── examples/              # Example scripts and outputs
│   └── script.txt         # Sample automation script
└── docs/                  # Documentation
```

## Quick Start

0. **uenv**

source /Users/rs/mouse/.venv/bin/activate

1. **Record automation sessions:**

   ```bash
   ./bin/record
   ```

   Interactive recording tool - middle click to start/stop recording your actions.

2. **Create automation scripts:**
   Create a text file with human-readable commands:

   ```
   move mouse to button1
   left click
   type "Hello World"
   press return

   type code block
   ```

   import sys
   class Example:
   def **init**(self):
   pass

   ```

   ```

3. **Run automation scripts:**

   ```bash
   # Play a regular script file (requires --locations argument)
   ./bin/play examples/script.txt --locations path/to/locations.json

   # Or play a recorded session (automatically uses session locations)
   ./bin/play rec1
   ```

   Press middle mouse button to start execution.

4. **Remap recordings for different machines:**

   ```bash
   # Remap a recording to adapt locations for your screen
   ./bin/remap rec1
   
   # Or specify a custom target directory
   ./bin/remap rec1 --remap-to my_custom_recording
   ```

   The remapper will guide you through clicking each location to update it for your machine.

## Features

### Session Recording (`src/core/script_recorder.py`)

- Interactive recording of mouse and keyboard actions
- Automatic location detection and naming
- Creates complete automation sessions with metadata

### Script Automation (`src/core/simon_says.py`)

- Human-readable command syntax
- Clipboard-based text pasting (reliable for code editors)
- Middle mouse button trigger for precise timing
- Automatic trailing whitespace cleanup

### Recording Remapper (`bin/remap`)

- Adapt recordings from one machine to another
- Interactive location remapping interface
- Preserves script logic while updating screen coordinates
- Creates new recording with updated locations

### Commands Supported

- `left click [at <location>]`
- `right click [at <location>]`
- `move mouse to <location>`
- `type "text"`
- `type line "text"` (adds return)
- `press <key>` (return, escape, tab, etc.)
- `wait <seconds>`
- `type code block` with `...` syntax

## Technical Details

- Uses macOS Quartz framework for precise input simulation
- Clipboard-based pasting avoids character encoding issues
- Home key navigation prevents auto-indent conflicts
- Middle mouse button trigger provides user control over execution timing
- Recording system automatically saves locations per session

## Requirements

- macOS with accessibility permissions
- Python 3.7+
- Quartz framework (built into macOS)

## Installation

1. Clone or download this project
2. Grant accessibility permissions to Terminal/Python
3. Record automation sessions with `./bin/record`
4. Play back recordings with `./bin/play <recording_id>` or run scripts with `./bin/play <script_file> --locations <locations_file>`
