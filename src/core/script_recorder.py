#!/usr/bin/env python3
"""
Script Recorder - Records user actions and converts them to Simon Says script format
"""

import json
import time
import os
from datetime import datetime
from Quartz import (
    CGEventMaskBit, CGEventTapCreate, CGEventGetLocation, CGEventGetIntegerValueField,
    kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventRightMouseDown, kCGEventRightMouseUp,
    kCGEventMouseMoved, kCGEventKeyDown, kCGEventKeyUp, kCGKeyboardEventKeycode,
    kCGEventOtherMouseDown, kCGEventOtherMouseUp, kCGMouseEventButtonNumber,
    kCGSessionEventTap, kCGHeadInsertEventTap,
    CFRunLoopGetCurrent, CFRunLoopRun, CFRunLoopStop,
    CFMachPortCreateRunLoopSource, CFRunLoopAddSource, kCFRunLoopDefaultMode,
    CGEventGetFlags
)

# Key code to name mapping for common keys
KEYCODE_NAMES = {
    36: 'return',
    49: 'space',
    48: 'tab',
    53: 'escape',
    51: 'backspace',
    126: 'up',
    125: 'down',
    123: 'left',
    124: 'right',
    115: 'home',
    119: 'end',
    122: 'f1', 120: 'f2', 99: 'f3', 118: 'f4', 96: 'f5', 97: 'f6',
    98: 'f7', 100: 'f8', 101: 'f9', 109: 'f10', 103: 'f11', 111: 'f12'
}

# Regular character keycodes
CHAR_KEYCODES = {
    0: 'a', 11: 'b', 8: 'c', 2: 'd', 14: 'e', 3: 'f', 5: 'g', 4: 'h',
    34: 'i', 38: 'j', 40: 'k', 37: 'l', 46: 'm', 45: 'n', 31: 'o', 35: 'p',
    12: 'q', 15: 'r', 1: 's', 17: 't', 32: 'u', 9: 'v', 13: 'w', 7: 'x',
    16: 'y', 6: 'z',
    18: '1', 19: '2', 20: '3', 21: '4', 23: '5', 22: '6', 26: '7', 28: '8', 25: '9', 29: '0',
    47: '.', 43: ',', 44: '/', 41: ';', 39: "'", 33: '[', 30: ']', 42: '\\', 27: '-', 24: '=', 50: '`'
}

class ScriptRecorder:
    def __init__(self, locations_file=None):
        self.base_locations_file = locations_file
        self.locations = self.load_locations()
        self.events = []
        self.start_time = None
        self.is_recording = False
        self.current_text_buffer = ""
        self.last_event_time = 0
        self.click_counter = 1  # For generating location names
        self.locations_modified = False  # Track if we need to save locations
        self.recording_locations_file = None  # Separate locations file for this recording
        self.last_click_location = None  # Track last click location for moves
        self.mouse_down_time = None  # Track when mouse was pressed down
        self.mouse_down_location = None  # Track where mouse was pressed down
        self.mouse_down_button = None  # Track which button was pressed
        
    def load_locations(self):
        """Load existing locations to match clicks to named locations"""
        if self.base_locations_file and os.path.exists(self.base_locations_file):
            try:
                with open(self.base_locations_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def find_nearest_location(self, x, y, threshold=20):
        """Find the nearest saved location within threshold pixels"""
        nearest_name = None
        nearest_distance = float('inf')
        
        for name, loc in self.locations.items():
            distance = ((x - loc['x'])**2 + (y - loc['y'])**2)**0.5
            if distance < threshold and distance < nearest_distance:
                nearest_distance = distance
                nearest_name = name
        
        return nearest_name
    
    def save_new_location(self, x, y):
        """Save a new click location with an auto-generated name"""
        # Generate a unique location name
        while True:
            location_name = f"click_{self.click_counter}"
            if location_name not in self.locations:
                break
            self.click_counter += 1
        
        # Save the location
        self.locations[location_name] = {'x': x, 'y': y}
        self.locations_modified = True
        self.click_counter += 1
        
        return location_name
    
    def get_next_recording_id(self):
        """Get the next simple recording ID (rec1, rec2, etc.)"""
        if not os.path.exists("recordings"):
            os.makedirs("recordings", exist_ok=True)
            return "rec1"
        
        # Find existing recordings
        existing = []
        for item in os.listdir("recordings"):
            if os.path.isdir(f"recordings/{item}") and item.startswith("rec"):
                try:
                    num = int(item[3:])  # Extract number after "rec"
                    existing.append(num)
                except ValueError:
                    continue
        
        # Return next number
        if existing:
            return f"rec{max(existing) + 1}"
        else:
            return "rec1"
    
    def save_locations(self):
        """Save locations to the recording-specific locations file"""
        if self.locations_modified and self.recording_locations_file:
            try:
                with open(self.recording_locations_file, 'w') as f:
                    json.dump(self.locations, f, indent=2)
                print(f"💾 Recording locations saved to {self.recording_locations_file}")
            except Exception as e:
                print(f"⚠️  Error saving locations: {e}")
            self.locations_modified = False
    
    def flush_text_buffer(self):
        """Convert accumulated text to script commands"""
        if not self.current_text_buffer:
            return
        
        text = self.current_text_buffer.strip()
        if not text:
            self.current_text_buffer = ""
            return
        
        # Check if it's a single line or multiple lines
        lines = text.split('\n')
        
        if len(lines) == 1:
            # Single line - use type command
            command = f'type "{text}"'
            self.events.append(command)
            print(f"\n[Captured text: \"{text}\"]")
        else:
            # Multiple lines - use code block format
            self.events.append('type code block')
            self.events.append('```')
            for line in lines:
                self.events.append(line)
            self.events.append('```')
            print(f"\n[Captured code block: {len(lines)} lines]")
        
        self.current_text_buffer = ""
    
    def keycode_to_char(self, keycode, flags):
        """Convert keycode to character, considering modifiers"""
        # Check if it's a special key
        if keycode in KEYCODE_NAMES:
            return KEYCODE_NAMES[keycode], True  # True = special key
        
        # Check if it's a regular character
        if keycode in CHAR_KEYCODES:
            char = CHAR_KEYCODES[keycode]
            
            # Check for shift modifier
            if flags & 0x20000:  # Shift flag
                if char.isalpha():
                    return char.upper(), False
                else:
                    # Handle shifted symbols
                    shift_map = {
                        '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
                        '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
                        '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
                        ';': ':', "'": '"', ',': '<', '.': '>', '/': '?',
                        '`': '~'
                    }
                    return shift_map.get(char, char), False
            else:
                return char, False
        
        return None, False
    
    def handle_key_combination(self, keycode, flags, current_time):
        """Handle key combinations like cmd+s, ctrl+c, etc."""
        # Check for modifier keys
        cmd_pressed = bool(flags & 0x100000)  # Command key
        ctrl_pressed = bool(flags & 0x40000)   # Control key  
        shift_pressed = bool(flags & 0x20000)  # Shift key
        option_pressed = bool(flags & 0x80000) # Option key
        
        # Only handle combinations, not lone modifier keys
        if not (cmd_pressed or ctrl_pressed) or keycode in [55, 59, 56, 58]:  # Skip lone modifiers
            return False
            
        # Get the base key name
        key_name = CHAR_KEYCODES.get(keycode) or KEYCODE_NAMES.get(keycode)
        if not key_name:
            return False
        
        # Flush text buffer before key combination
        self.flush_text_buffer()
        
        # Build the combination command
        modifiers = []
        if cmd_pressed:
            modifiers.append("cmd")
        if ctrl_pressed:
            modifiers.append("ctrl")
        if shift_pressed:
            modifiers.append("shift")
        if option_pressed:
            modifiers.append("option")
            
        command = f"press {'+'.join(modifiers)}+{key_name}"
        self.events.append(command)
        print(f"[{current_time - self.start_time:.1f}s] {command}")
        
        return True  # Handled
    
    def event_callback(self, proxy, event_type, event, refcon):
        """Handle recorded events"""
        current_time = time.time()
        
        # Check for middle mouse click to toggle recording
        if event_type == kCGEventOtherMouseDown:
            button = CGEventGetIntegerValueField(event, kCGMouseEventButtonNumber)
            if button == 2:  # Middle mouse button (button 2)
                if not self.is_recording:
                    self.is_recording = True
                    self.start_time = current_time
                    self.events = []
                    self.current_text_buffer = ""
                    self.last_event_time = current_time
                    self.last_click_location = None
                    self.click_counter = 1
                    
                    # Create recording folder and files with simple counter
                    self.recording_id = self.get_next_recording_id()
                    self.recording_folder = f"recordings/{self.recording_id}"
                    
                    # Create recording folder
                    os.makedirs(self.recording_folder, exist_ok=True)
                    
                    self.recording_locations_file = f"{self.recording_folder}/locations.json"
                    
                    print("\n🔴 RECORDING STARTED - Middle click again to stop")
                    print(f"📍 Locations will be saved to: {self.recording_locations_file}")
                    print("Perform your actions...")
                    print("-" * 40)
                    return None  # Consume the middle click event
                else:
                    self.is_recording = False
                    print("-" * 40)
                    print("⏹ RECORDING STOPPED")
                    self.flush_text_buffer()  # Save any remaining text
                    self.save_script()
                    # Stop the run loop to exit
                    CFRunLoopStop(CFRunLoopGetCurrent())
                    return None  # Consume the middle click event
        
        # Only record events if recording is active
        if not self.is_recording:
            return event
        
        # Add wait commands for delays and flush text on pauses
        time_since_last = current_time - self.last_event_time
        if time_since_last > 0.5:  # More than 0.5 seconds indicates a pause
            # Flush any accumulated text before the wait
            if self.current_text_buffer.strip():
                self.flush_text_buffer()
                print(f"\n[Text flushed after pause]")
            
            # Add wait command if we have other events
            if self.events:
                # Round to nearest 0.25 second for more precise timing
                if time_since_last >= 2.0:
                    wait_time = 0.6  # 0.5 * 1.25
                elif time_since_last >= 1.0:
                    wait_time = 0.4  # 0.3 * 1.25 (rounded)
                else:
                    wait_time = 0.25  # 0.2 * 1.25
                
                self.events.append(f"wait {wait_time}")
                print(f"[Added wait {wait_time}s]")
        
        self.last_event_time = current_time
        
        # Handle mouse clicks
        if event_type in [kCGEventLeftMouseDown, kCGEventLeftMouseUp, 
                         kCGEventRightMouseDown, kCGEventRightMouseUp]:
            
            loc = CGEventGetLocation(event)
            x, y = int(loc.x), int(loc.y)
            
            # Handle mouse down events - start tracking for potential drag
            if event_type in [kCGEventLeftMouseDown, kCGEventRightMouseDown]:
                # Flush any pending text before mouse action
                self.flush_text_buffer()
                
                button = 'left' if event_type == kCGEventLeftMouseDown else 'right'
                
                # Start tracking this mouse down for potential drag
                self.mouse_down_time = current_time
                self.mouse_down_button = button
                
                # Try to find an existing nearby location
                location_name = self.find_nearest_location(x, y)
                
                if not location_name:
                    # Save new location and use it
                    location_name = self.save_new_location(x, y)
                    print(f"[{current_time - self.start_time:.1f}s] Saved new location '{location_name}' at ({x}, {y})")
                
                self.mouse_down_location = location_name
                
                # Add mouse movement if we have a previous click location
                if self.last_click_location and self.last_click_location != location_name:
                    move_command = f"move mouse to {location_name}"
                    self.events.append(move_command)
                    print(f"[{current_time - self.start_time:.1f}s] {move_command}")
                
                print(f"[{current_time - self.start_time:.1f}s] Mouse down at {location_name} - waiting for release...")
                
            # Handle mouse up events - determine if it was click or drag
            elif event_type in [kCGEventLeftMouseUp, kCGEventRightMouseUp]:
                if self.mouse_down_time is not None:
                    hold_duration = current_time - self.mouse_down_time
                    button = 'left' if event_type == kCGEventLeftMouseUp else 'right'
                    
                    # Find location for mouse up position
                    up_location_name = self.find_nearest_location(x, y)
                    if not up_location_name:
                        up_location_name = self.save_new_location(x, y)
                        print(f"[{current_time - self.start_time:.1f}s] Saved new location '{up_location_name}' at ({x}, {y})")
                    
                    # Determine if this was a click, hold, or drag
                    if hold_duration > 0.5:  # Held for more than 0.5 seconds
                        if self.mouse_down_location == up_location_name:
                            # Click and hold (same location)
                            command = f"{button} click and hold at {self.mouse_down_location} for {hold_duration:.1f}s"
                        else:
                            # Drag operation (different locations)  
                            command = f"drag {button} from {self.mouse_down_location} to {up_location_name}"
                    else:
                        # Quick click
                        command = f"{button} click at {self.mouse_down_location}"
                    
                    self.events.append(command)
                    print(f"[{current_time - self.start_time:.1f}s] {command}")
                    
                    # Add automatic safety delay after mouse action
                    self.events.append("wait 0.25") 
                    print(f"[Added UI safety delay: 0.25s]")
                    
                    # Remember this location for next move
                    self.last_click_location = up_location_name
                    
                    # Reset tracking
                    self.mouse_down_time = None
                    self.mouse_down_location = None
                    self.mouse_down_button = None
        
        # Handle keyboard events
        elif event_type in [kCGEventKeyDown, kCGEventKeyUp]:
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            flags = CGEventGetFlags(event)
            
            # No need to skip any keys now since we're using middle click
            
            # Only process key down events
            if event_type == kCGEventKeyDown:
                # Check for modifier key combinations first
                if self.handle_key_combination(keycode, flags, current_time):
                    return event
                
                char, is_special = self.keycode_to_char(keycode, flags)
                
                if char:
                    if is_special:
                        # Handle special keys that affect text
                        if char in ['backspace', 'delete']:
                            # Handle delete keys - remove from buffer if possible
                            if self.current_text_buffer and char == 'backspace':
                                self.current_text_buffer = self.current_text_buffer[:-1]
                                print("⌫", end="", flush=True)
                            else:
                                # Flush buffer and record the delete key
                                self.flush_text_buffer()
                                command = f"press {char}"
                                self.events.append(command)
                                print(f"[{current_time - self.start_time:.1f}s] {command}")
                        else:
                            # Other special keys - flush text buffer and add press command
                            self.flush_text_buffer()
                            command = f"press {char}"
                            self.events.append(command)
                            print(f"[{current_time - self.start_time:.1f}s] {command}")
                            
                            # Add automatic delay after return keys for code editors
                            if char == 'return':
                                self.events.append("wait 0.25")
                                print(f"[Added return delay: 0.25s]")
                    else:
                        # Regular character - add to text buffer silently
                        self.current_text_buffer += char
                        print(".", end="", flush=True)  # Simple progress indicator
        
        return event
    
    def save_script(self):
        """Save the recorded events as a Simon Says script"""
        if not self.events:
            print("No events recorded")
            return
        
        # Save locations if they were modified
        self.save_locations()
        
        # Save to recording folder
        script_filename = f"{self.recording_folder}/script.txt"
        
        # Count new locations created
        new_locations = self.click_counter - 1
        
        # Add header comment
        script_lines = [
            f"# Recording ID: {self.recording_id}",
            f"# Recorded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Duration: {time.time() - self.start_time:.1f} seconds",
            f"# Total commands: {len(self.events)}",
            f"# New locations saved: {new_locations}",
            "",
            f"# To run this recording:",
            f"# ./bin/play {self.recording_id}",
            "",
        ]
        
        # Add events
        script_lines.extend(self.events)
        
        # Write script file
        with open(script_filename, 'w') as f:
            f.write('\n'.join(script_lines))
        
        # Create a summary file
        summary_filename = f"{self.recording_folder}/info.json"
        summary_data = {
            "id": self.recording_id,
            "created": datetime.now().isoformat(),
            "duration": time.time() - self.start_time,
            "commands": len(self.events),
            "locations": new_locations,
            "description": f"Recording from {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        with open(summary_filename, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"\n✅ Recording saved: {self.recording_id}")
        print(f"📁 Folder: {self.recording_folder}")
        print(f"📝 Commands: {len(self.events)}")
        print(f"📍 New locations: {new_locations}")
        print(f"⏱️ Duration: {time.time() - self.start_time:.1f} seconds")
        print(f"\n🚀 To run: ./bin/play {self.recording_id}")
    
    def start_recording(self):
        """Start the recording session"""
        print("=== Script Recorder ===")
        print("This tool records your actions and converts them to Simon Says script format")
        print("")
        print("Instructions:")
        print("1. Middle click to start recording")
        print("2. Perform your actions (clicks, typing, etc.)")
        print("3. Middle click again to stop and save the script")
        print("4. Press Ctrl+C to exit")
        print("")
        if self.locations:
            print(f"📍 Loaded {len(self.locations)} saved locations for smart click detection")
        print("-" * 60)
        
        # Listen for mouse clicks and keyboard events
        mask = (
            CGEventMaskBit(kCGEventLeftMouseDown) |
            CGEventMaskBit(kCGEventLeftMouseUp) |
            CGEventMaskBit(kCGEventRightMouseDown) |
            CGEventMaskBit(kCGEventRightMouseUp) |
            CGEventMaskBit(kCGEventOtherMouseDown) |
            CGEventMaskBit(kCGEventOtherMouseUp) |
            CGEventMaskBit(kCGEventKeyDown) |
            CGEventMaskBit(kCGEventKeyUp)
        )
        
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            0,
            mask,
            self.event_callback,
            None
        )
        
        if not tap:
            print("❌ Failed to create event tap. Check accessibility permissions:")
            print("   System Settings > Privacy & Security > Privacy > Accessibility")
            print("   Add Terminal/Python to allowed apps")
            return False
        
        try:
            source = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopDefaultMode)
            CFRunLoopRun()
        except KeyboardInterrupt:
            print("\n\n👋 Recorder stopped")
            if self.is_recording:
                print("⚠️  Recording was in progress but not saved")
            CFRunLoopStop(CFRunLoopGetCurrent())
        
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Record actions and convert to Simon Says script format')
    parser.add_argument('--locations',
                       help='Base locations file for smart click detection (optional)')
    
    args = parser.parse_args()
    
    recorder = ScriptRecorder(args.locations)
    recorder.start_recording()

if __name__ == '__main__':
    main()