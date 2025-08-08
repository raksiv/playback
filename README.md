# Mouse Automation Suite

A collection of tools for mouse and keyboard automation on macOS, including location learning, script recording/playback, and human-readable automation scripts.

## Project Structure

```
/
├── bin/                    # Executable wrapper scripts
│   ├── learn              # Quick access to location learning
│   └── play               # Quick access to script execution
├── src/
│   ├── core/              # Main functionality
│   │   ├── learn.py       # Learn and save screen locations
│   │   └── simon_says.py  # Execute human-readable automation scripts
│   └── tools/             # Utilities and helpers
│       ├── position.py    # Position utilities
│       └── main.py        # Additional tools
├── examples/              # Example scripts and outputs
│   └── script.txt         # Sample automation script
├── docs/                  # Documentation
└── locations.json         # Saved screen locations
```

## Quick Start

1. **Learn screen locations:**
   ```bash
   ./bin/learn
   ```
   Interactive tool to click and name UI elements.

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
       def __init__(self):
           pass
   ```
   ```

3. **Run automation scripts:**
   ```bash
   ./bin/play examples/script.txt
   ```
   Press F1 to start execution.

## Features

### Location Learning (`src/core/learn.py`)
- Interactive GUI for learning screen coordinates
- Save/load named locations to JSON
- Commands: `learn <name>`, `list`, `delete <name>`

### Script Automation (`src/core/simon_says.py`)
- Human-readable command syntax
- Clipboard-based text pasting (reliable for code editors)
- F1 trigger for precise timing
- Automatic trailing whitespace cleanup

### Commands Supported
- `left click [at <location>]`
- `right click [at <location>]` 
- `move mouse to <location>`
- `type "text"`
- `type line "text"` (adds return)
- `press <key>` (return, escape, tab, etc.)
- `wait <seconds>`
- `type code block` with ```...``` syntax

## Technical Details

- Uses macOS Quartz framework for precise input simulation
- Clipboard-based pasting avoids character encoding issues
- Home key navigation prevents auto-indent conflicts
- F1 trigger provides user control over execution timing

## Requirements

- macOS with accessibility permissions
- Python 3.7+
- Quartz framework (built into macOS)

## Installation

1. Clone or download this project
2. Grant accessibility permissions to Terminal/Python
3. Run `./bin/learn` to start learning locations
4. Create automation scripts and run with `./bin/play`