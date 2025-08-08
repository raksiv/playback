#!/usr/bin/env python3
"""
Simon Says using clipboard paste approach - much more reliable for code editors
"""

import json
import time
import os
import re
import subprocess
from Quartz import (
    CGEventCreateMouseEvent, CGEventCreateKeyboardEvent,
    CGEventPost, kCGHIDEventTap, CGPointMake,
    kCGEventLeftMouseDown, kCGEventLeftMouseUp,
    kCGEventRightMouseDown, kCGEventRightMouseUp,
    kCGEventMouseMoved,
    kCGMouseButtonLeft, kCGMouseButtonRight,
    CGEventCreate, CGEventGetLocation,
    CGEventKeyboardSetUnicodeString
)

# Key codes for common keys
KEYCODES = {
    'a': 0, 'b': 11, 'c': 8, 'd': 2, 'e': 14, 'f': 3, 'g': 5, 'h': 4,
    'i': 34, 'j': 38, 'k': 40, 'l': 37, 'm': 46, 'n': 45, 'o': 31, 'p': 35,
    'q': 12, 'r': 15, 's': 1, 't': 17, 'u': 32, 'v': 9, 'w': 13, 'x': 7,
    'y': 16, 'z': 6,
    '0': 29, '1': 18, '2': 19, '3': 20, '4': 21, '5': 23, '6': 22, '7': 26,
    '8': 28, '9': 25,
    'space': 49, 'return': 36, 'enter': 36, 'tab': 48, 'escape': 53, 'esc': 53,
    'delete': 51, 'backspace': 51,
    'up': 126, 'down': 125, 'left': 123, 'right': 124,
    'home': 115, 'end': 119,  # Home and End keys
    'shift': 56, 'cmd': 55, 'command': 55, 'ctrl': 59, 'control': 59,
    'option': 58, 'alt': 58,
    '.': 47, ',': 43, '/': 44, ';': 41, "'": 39, '[': 33, ']': 30,
    '\\': 42, '-': 27, '=': 24, '`': 50,
    'f1': 122, 'f2': 120, 'f3': 99, 'f4': 118, 'f5': 96, 'f6': 97,
    'f7': 98, 'f8': 100, 'f9': 101, 'f10': 109, 'f11': 103, 'f12': 111
}

# Shift key mappings
SHIFT_CHARS = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7',
    '*': '8', '(': '9', ')': '0', '_': '-', '+': '=', '{': '[', '}': ']',
    '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/', '~': '`',
    ' ': 'space', '\n': 'return', '\t': 'tab'
}

class SimonSaysPaste:
    def __init__(self, locations_file, delay=0.06):
        self.locations = {}
        self.delay = delay
        self.load_locations(locations_file)
        
    def load_locations(self, locations_file):
        """Load saved locations from file"""
        if os.path.exists(locations_file):
            try:
                with open(locations_file, 'r') as f:
                    self.locations = json.load(f)
                    print(f"Loaded {len(self.locations)} locations")
            except:
                print(f"Warning: Could not load locations from {locations_file}")
                self.locations = {}
        else:
            print(f"Warning: No locations file found at {locations_file}")
    
    def get_current_mouse_position(self):
        """Get current mouse position"""
        event = CGEventCreate(None)
        loc = CGEventGetLocation(event)
        return int(loc.x), int(loc.y)
    
    def move_mouse(self, x, y, smooth=True, duration=0.2):
        """Move mouse to specific coordinates with smooth animation"""
        if not smooth:
            # Instant movement (old behavior)
            point = CGPointMake(x, y)
            move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, point, 0)
            CGEventPost(kCGHIDEventTap, move_event)
            time.sleep(0.1)
            return
        
        # Get current position
        current_x, current_y = self.get_current_mouse_position()
        
        # Calculate distance and steps
        distance = ((x - current_x)**2 + (y - current_y)**2)**0.5
        
        # Determine number of steps based on distance (more steps for longer distances)
        steps = max(10, min(int(distance / 10), 30))  # Between 10-30 steps
        
        # Calculate step increments
        dx = (x - current_x) / steps
        dy = (y - current_y) / steps
        step_delay = duration / steps
        
        # Animate movement
        for i in range(steps + 1):
            intermediate_x = current_x + (dx * i)
            intermediate_y = current_y + (dy * i)
            
            point = CGPointMake(intermediate_x, intermediate_y)
            move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, point, 0)
            CGEventPost(kCGHIDEventTap, move_event)
            time.sleep(step_delay)
    
    def click_mouse(self, button='left', x=None, y=None):
        """Click mouse button at current or specified position"""
        if x is not None and y is not None:
            self.move_mouse(x, y)
            time.sleep(0.05)  # Give UI time to respond to mouse movement
        
        current_x, current_y = self.get_current_mouse_position()
        point = CGPointMake(current_x, current_y)
        
        if button == 'left':
            down_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, point, kCGMouseButtonLeft)
            up_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, point, kCGMouseButtonLeft)
        elif button == 'right':
            down_event = CGEventCreateMouseEvent(None, kCGEventRightMouseDown, point, kCGMouseButtonRight)
            up_event = CGEventCreateMouseEvent(None, kCGEventRightMouseUp, point, kCGMouseButtonRight)
        else:
            print(f"Unknown button: {button}")
            return
        
        CGEventPost(kCGHIDEventTap, down_event)
        time.sleep(0.1)  # Longer click duration
        CGEventPost(kCGHIDEventTap, up_event)
        time.sleep(0.1)
    
    def click_and_hold(self, button='left', duration=0.4, x=None, y=None):
        """Click and hold mouse button for specified duration"""
        if x is not None and y is not None:
            self.move_mouse(x, y)
            time.sleep(0.05)
        
        current_x, current_y = self.get_current_mouse_position()
        point = CGPointMake(current_x, current_y)
        
        if button == 'left':
            down_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, point, kCGMouseButtonLeft)
            up_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, point, kCGMouseButtonLeft)
        elif button == 'right':
            down_event = CGEventCreateMouseEvent(None, kCGEventRightMouseDown, point, kCGMouseButtonRight)
            up_event = CGEventCreateMouseEvent(None, kCGEventRightMouseUp, point, kCGMouseButtonRight)
        else:
            print(f"Unknown button: {button}")
            return
        
        # Press and hold
        CGEventPost(kCGHIDEventTap, down_event)
        time.sleep(duration)  # Hold for specified duration
        CGEventPost(kCGHIDEventTap, up_event)
        time.sleep(0.05)
    
    def drag_mouse(self, button='left', from_x=None, from_y=None, to_x=None, to_y=None):
        """Drag mouse from one location to another"""
        # Move to start position
        if from_x is not None and from_y is not None:
            self.move_mouse(from_x, from_y)
            time.sleep(0.05)
        
        start_x, start_y = self.get_current_mouse_position()
        start_point = CGPointMake(start_x, start_y)
        
        # Mouse down at start position
        if button == 'left':
            down_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, start_point, kCGMouseButtonLeft)
        elif button == 'right':
            down_event = CGEventCreateMouseEvent(None, kCGEventRightMouseDown, start_point, kCGMouseButtonRight)
        else:
            print(f"Unknown button: {button}")
            return
        
        CGEventPost(kCGHIDEventTap, down_event)
        time.sleep(0.1)
        
        # Drag to end position
        if to_x is not None and to_y is not None:
            self.move_mouse(to_x, to_y, smooth=True, duration=0.25)  # Slower drag movement
        
        # Mouse up at end position
        end_x, end_y = self.get_current_mouse_position()
        end_point = CGPointMake(end_x, end_y)
        
        if button == 'left':
            up_event = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, end_point, kCGMouseButtonLeft)
        elif button == 'right':
            up_event = CGEventCreateMouseEvent(None, kCGEventRightMouseUp, end_point, kCGMouseButtonRight)
        
        CGEventPost(kCGHIDEventTap, up_event)
        time.sleep(0.05)
    
    def release_all_modifiers(self):
        """Force release ALL modifier keys to prevent stuck states"""
        modifiers = [
            (55, 'cmd'),
            (56, 'shift'), 
            (57, 'caps lock'),
            (58, 'option/alt'),
            (59, 'control'),
            (60, 'right shift'),
            (61, 'right option'),
            (62, 'right control'),
            (63, 'fn')  # Function key - THIS is the problematic one!
        ]
        
        for keycode, name in modifiers:
            try:
                # Send key up event for each modifier
                up_event = CGEventCreateKeyboardEvent(None, keycode, False)
                CGEventPost(kCGHIDEventTap, up_event)
            except:
                pass  # Ignore errors for non-existent keycodes
        
        # Small delay to ensure all releases are processed
        time.sleep(0.01)
    
    
    def press_key_combo(self, key, cmd=False, ctrl=False, shift=False, option=False):
        """Press a key combination"""
        if key not in KEYCODES:
            print(f"Unknown key: {key}")
            return
        
        keycode = KEYCODES[key]
        
        # Press modifiers
        if cmd:
            cmd_down = CGEventCreateKeyboardEvent(None, 55, True)
            CGEventPost(kCGHIDEventTap, cmd_down)
        if ctrl:
            ctrl_down = CGEventCreateKeyboardEvent(None, 59, True)
            CGEventPost(kCGHIDEventTap, ctrl_down)
        if shift:
            shift_down = CGEventCreateKeyboardEvent(None, 56, True)
            CGEventPost(kCGHIDEventTap, shift_down)
        if option:
            option_down = CGEventCreateKeyboardEvent(None, 58, True)
            CGEventPost(kCGHIDEventTap, option_down)
        
        time.sleep(0.005)
        
        # Press main key
        key_down = CGEventCreateKeyboardEvent(None, keycode, True)
        CGEventPost(kCGHIDEventTap, key_down)
        time.sleep(0.005)
        
        key_up = CGEventCreateKeyboardEvent(None, keycode, False)
        CGEventPost(kCGHIDEventTap, key_up)
        time.sleep(0.005)
        
        # Release modifiers in reverse order
        if option:
            option_up = CGEventCreateKeyboardEvent(None, 58, False)
            CGEventPost(kCGHIDEventTap, option_up)
        if shift:
            shift_up = CGEventCreateKeyboardEvent(None, 56, False)
            CGEventPost(kCGHIDEventTap, shift_up)
        if ctrl:
            ctrl_up = CGEventCreateKeyboardEvent(None, 59, False)
            CGEventPost(kCGHIDEventTap, ctrl_up)
        if cmd:
            cmd_up = CGEventCreateKeyboardEvent(None, 55, False)
            CGEventPost(kCGHIDEventTap, cmd_up)
        
        time.sleep(0.005)
    
    
    def type_key(self, key):
        """Type a single key"""
        if key not in KEYCODES:
            print(f"Unknown key: {key}")
            return
        
        # CRITICAL: Release ALL modifiers before typing 'e', '.', or 'd' to prevent emoji picker
        # Fn+E, Fn+., and Fn+D can trigger the emoji picker on macOS
        if key in ['e', '.', 'd']:
            self.release_all_modifiers()
        
        keycode = KEYCODES[key]
        
        # Special handling for return key with longer timing
        if key == 'return':
            down_event = CGEventCreateKeyboardEvent(None, keycode, True)
            CGEventPost(kCGHIDEventTap, down_event)
            time.sleep(0.1)  # Longer press duration
            
            up_event = CGEventCreateKeyboardEvent(None, keycode, False)
            CGEventPost(kCGHIDEventTap, up_event)
            time.sleep(0.05)
            
        else:
            # Standard key handling
            down_event = CGEventCreateKeyboardEvent(None, keycode, True)
            CGEventPost(kCGHIDEventTap, down_event)
            time.sleep(0.01)
            
            up_event = CGEventCreateKeyboardEvent(None, keycode, False)
            CGEventPost(kCGHIDEventTap, up_event)
            time.sleep(0.01)
    
    def release_all_modifiers(self):
        """Release all modifier keys to prevent race conditions"""
        modifiers = [
            (55, 'cmd'), 
            (59, 'ctrl'), 
            (56, 'shift'), 
            (58, 'option'),
            (63, 'fn')  # Function key - this could be the culprit!
        ]
        for keycode, name in modifiers:
            try:
                up_event = CGEventCreateKeyboardEvent(None, keycode, False)
                CGEventPost(kCGHIDEventTap, up_event)
            except:
                pass
        time.sleep(0.005)
    
    def type_text(self, text):
        """Type text character by character (fallback for simple text)"""
        for i, char in enumerate(text):
            # Extra safety: release modifiers before ANY 'e', '.', or 'd' character
            if char.lower() in ['e', 'd'] or char == '.':
                self.release_all_modifiers()
            
            if char == ' ':
                self.type_key('space')
            elif char == '\n':
                self.type_key('return')
            elif char == '\t':
                self.type_key('tab')
            elif char in SHIFT_CHARS and char not in [' ', '\n', '\t']:
                base_key = SHIFT_CHARS[char]
                if base_key in KEYCODES:
                    self.press_key_combo(base_key, shift=True)
            elif char.isupper():
                # For uppercase E and D, be extra careful
                if char in ['E', 'D']:
                    self.release_all_modifiers()
                    time.sleep(0.05)
                self.press_key_combo(char.lower(), shift=True)
            elif char.lower() in KEYCODES:
                self.type_key(char.lower())
            else:
                print(f"Cannot type character: {char}")
            time.sleep(0.005)
    
    def execute_command(self, command):
        """Execute a single command"""
        command = command.strip()
        
        if not command or command.startswith('#'):
            return
        
        print(f"Executing: {command}")
        
        if command.lower().startswith('left click and hold'):
            # Parse: "left click and hold at location for 2.5s"
            parts = command.lower().split('at', 1)
            if len(parts) > 1:
                location_and_duration = parts[1].strip()
                if 'for' in location_and_duration:
                    location, duration_part = location_and_duration.split('for', 1)
                    location = location.strip()
                    duration_str = duration_part.strip().rstrip('s')
                    try:
                        duration = float(duration_str)
                    except:
                        duration = 0.4
                else:
                    location = location_and_duration
                    duration = 1.0
                
                if location in self.locations:
                    loc = self.locations[location]
                    self.click_and_hold('left', duration, loc['x'], loc['y'])
                else:
                    print(f"Unknown location: {location}")
            else:
                self.click_and_hold('left', 1.0)
                
        elif command.lower().startswith('right click and hold'):
            # Parse: "right click and hold at location for 2.5s"
            parts = command.lower().split('at', 1)
            if len(parts) > 1:
                location_and_duration = parts[1].strip()
                if 'for' in location_and_duration:
                    location, duration_part = location_and_duration.split('for', 1)
                    location = location.strip()
                    duration_str = duration_part.strip().rstrip('s')
                    try:
                        duration = float(duration_str)
                    except:
                        duration = 0.4
                else:
                    location = location_and_duration
                    duration = 1.0
                
                if location in self.locations:
                    loc = self.locations[location]
                    self.click_and_hold('right', duration, loc['x'], loc['y'])
                else:
                    print(f"Unknown location: {location}")
            else:
                self.click_and_hold('right', 1.0)
                
        elif command.lower().startswith('drag left from') or command.lower().startswith('drag right from'):
            # Parse: "drag left from location1 to location2"
            button = 'left' if 'drag left' in command.lower() else 'right'
            parts = command.lower().split('from', 1)[1].strip()
            if 'to' in parts:
                from_loc, to_loc = parts.split('to', 1)
                from_loc = from_loc.strip()
                to_loc = to_loc.strip()
                
                if from_loc in self.locations and to_loc in self.locations:
                    from_pos = self.locations[from_loc]
                    to_pos = self.locations[to_loc]
                    self.drag_mouse(button, from_pos['x'], from_pos['y'], to_pos['x'], to_pos['y'])
                else:
                    print(f"Unknown location: {from_loc} or {to_loc}")
            else:
                print("Drag command missing 'to' location")
                
        elif command.lower().startswith('left click'):
            if 'at' in command:
                parts = command.split('at', 1)[1].strip()
                if parts in self.locations:
                    loc = self.locations[parts]
                    self.click_mouse('left', loc['x'], loc['y'])
                else:
                    print(f"Unknown location: {parts}")
            else:
                self.click_mouse('left')
                
        elif command.lower().startswith('right click'):
            if 'at' in command:
                parts = command.split('at', 1)[1].strip()
                if parts in self.locations:
                    loc = self.locations[parts]
                    self.click_mouse('right', loc['x'], loc['y'])
                else:
                    print(f"Unknown location: {parts}")
            else:
                self.click_mouse('right')
                
        elif command.lower().startswith('move mouse to'):
            location = command[13:].strip()
            if location in self.locations:
                loc = self.locations[location]
                self.move_mouse(loc['x'], loc['y'])
            else:
                match = re.match(r'\(?\s*(\d+)\s*,\s*(\d+)\s*\)?', location)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    self.move_mouse(x, y)
                else:
                    print(f"Unknown location: {location}")
                    
        elif command.lower().startswith('press'):
            key_combo = command[5:].strip()
            
            # Check if it's a key combination (contains +)
            if '+' in key_combo:
                parts = key_combo.split('+')
                modifiers = parts[:-1]  # All but last are modifiers
                key = parts[-1].strip().lower()
                
                # Convert modifier names
                cmd = 'cmd' in modifiers or 'command' in modifiers
                ctrl = 'ctrl' in modifiers or 'control' in modifiers  
                shift = 'shift' in modifiers
                option = 'option' in modifiers or 'alt' in modifiers
                
                if key in KEYCODES:
                    print(f"  Pressing key combo: {key_combo}")
                    self.press_key_combo(key, cmd=cmd, ctrl=ctrl, shift=shift, option=option)
                else:
                    print(f"Unknown key in combo: {key}")
            else:
                # Simple key press
                key = key_combo.lower()
                if key in KEYCODES:
                    print(f"  Pressing key: '{key}'")
                    self.type_key(key)
                else:
                    print(f"Unknown key: {key}")
                    
        elif command.lower().startswith('newline') or command.lower() == 'new line':
            # Alternative newline method for problematic editors
            print("  Creating newline (clipboard method)")
            self.copy_to_clipboard('\n')
            time.sleep(0.05)
            self.press_key_combo('v', cmd=True)
            time.sleep(0.05)
            
        elif command.lower().startswith('paste newline') or command.lower().startswith('paste line'):
            # Paste text with newline at the end using clipboard
            if 'paste line' in command.lower():
                text = command.split('paste line', 1)[1].strip()
            else:
                text = command.split('paste newline', 1)[1].strip()
            
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            
            print(f"  Pasting line with newline: '{text}'")
            self.copy_to_clipboard(text + '\n')
            time.sleep(0.05)
            self.press_key_combo('v', cmd=True)
            time.sleep(0.05)
                
        elif command.lower().startswith('type line'):
            text = command[9:].strip()
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            self.type_text(text)
            self.type_key('return')
            
        elif command.lower().startswith('type'):
            text = command[4:].strip()
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            self.type_text(text)
            
        elif command.lower().startswith('wait') or command.lower().startswith('sleep'):
            match = re.search(r'(\d+(?:\.\d+)?)', command)
            if match:
                duration = float(match.group(1))
                time.sleep(duration)
            else:
                time.sleep(1)
                
        else:
            print(f"Unknown command: {command}")
    
    def execute_script(self, script_text):
        """Execute a script with multiple commands"""
        try:
            lines = script_text.split('\n')
            i = 0
            
            while i < len(lines):
                line_stripped = lines[i].strip()
                
                # Skip empty lines and comments
                if not line_stripped or line_stripped.startswith('#'):
                    i += 1
                    continue
                
                # Check for code block command
                if line_stripped.lower() == 'type code block' or line_stripped.lower().startswith('type code block'):
                    i += 1
                    code_block = []
                    
                    # Look for the opening ```
                    while i < len(lines) and lines[i].strip() != '```':
                        i += 1
                    
                    if i < len(lines):
                        i += 1  # Skip the opening ```
                        
                        # Collect lines until closing ```
                        while i < len(lines) and not (lines[i].strip() == '```'):
                            # Keep the exact line with all formatting
                            code_block.append(lines[i])
                            i += 1
                        
                        # Paste the code block line by line
                        if code_block:
                            print(f"Pasting code block ({len(code_block)} lines)")
                            
                            for idx, code_line in enumerate(code_block):
                                print(f"  Line {idx+1}: '{code_line}'")
                                
                                # Paste the line (this handles indentation properly)
                                self.paste_line(code_line)
                                
                                # Press return to go to next line
                                self.type_key('return')
                                time.sleep(0.05)
                            
                            time.sleep(self.delay)
                        
                        i += 1  # Skip the closing ```
                else:
                    # Regular command
                    self.execute_command(line_stripped)
                    time.sleep(self.delay)
                    i += 1
        
        except KeyboardInterrupt:
            print("\n🛑 Playback stopped by user")
            return
        
        print("Script execution completed")
    
    def execute_file(self, filename):
        """Execute commands from a file"""
        try:
            with open(filename, 'r') as f:
                script = f.read()
            print(f"Executing script from {filename}")
            self.execute_script(script)
            print("Script execution completed")
        except FileNotFoundError:
            print(f"Script file not found: {filename}")
        except Exception as e:
            print(f"Error executing script: {e}")

def wait_for_middle_click():
    """Wait for middle mouse click to start execution"""
    from Quartz import (
        CGEventMaskBit, CGEventTapCreate, CGEventGetIntegerValueField,
        kCGEventOtherMouseDown, kCGMouseEventButtonNumber,
        kCGSessionEventTap, kCGHeadInsertEventTap,
        CFRunLoopGetCurrent, CFRunLoopRun, CFRunLoopStop,
        CFMachPortCreateRunLoopSource, CFRunLoopAddSource, kCFRunLoopDefaultMode
    )
    
    middle_clicked = [False]  # Use list for closure
    
    def middle_click_callback(proxy, event_type, event, refcon):
        if event_type == kCGEventOtherMouseDown:
            button = CGEventGetIntegerValueField(event, kCGMouseEventButtonNumber)
            if button == 2:  # Middle mouse button
                middle_clicked[0] = True
                CFRunLoopStop(CFRunLoopGetCurrent())
                return None  # Consume the middle click event
        return event
    
    print("Middle click to start execution...")
    print("Press Ctrl+C to cancel")
    
    # Create event tap for middle mouse click
    mask = CGEventMaskBit(kCGEventOtherMouseDown)
    tap = CGEventTapCreate(
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        0,
        mask,
        middle_click_callback,
        None
    )
    
    if not tap:
        print("Failed to create event tap. Check accessibility permissions.")
        return False
    
    try:
        source = CFMachPortCreateRunLoopSource(None, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopDefaultMode)
        CFRunLoopRun()
        return middle_clicked[0]
    except KeyboardInterrupt:
        print("\nCancelled by user")
        CFRunLoopStop(CFRunLoopGetCurrent())
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Execute commands using clipboard paste approach')
    parser.add_argument('script', nargs='?', help='Script file to execute')
    parser.add_argument('--locations', 
                       help='Locations file (required for recorded scripts)')
    parser.add_argument('--delay', type=float, default=0.06, 
                       help='Delay between commands in seconds (default: 0.1)')
    parser.add_argument('--countdown', action='store_true',
                       help='Use countdown instead of middle click trigger')
    
    args = parser.parse_args()
    
    if args.script:
        # Check if it's a recording ID or a file path
        if os.path.exists(f"recordings/{args.script}/script.txt"):
            # It's a recording ID
            recording_id = args.script
            script_file = f"recordings/{recording_id}/script.txt"
            locations_file = f"recordings/{recording_id}/locations.json"
            
            # Create SimonSaysPaste with recording-specific locations
            simon = SimonSaysPaste(locations_file, args.delay)
            
            # Load info
            info_file = f"recordings/{recording_id}/info.json"
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    info = json.load(f)
                print(f"🎬 Playing recording: {recording_id}")
                print(f"📅 Created: {info.get('created', 'unknown')}")
                print(f"⏱️ Duration: {info.get('duration', 0):.1f}s")
                print(f"📝 Commands: {info.get('commands', 0)}")
            else:
                print(f"🎬 Playing recording: {recording_id}")
        
        elif os.path.exists(args.script):
            # It's a regular file path
            script_file = args.script
            if not args.locations:
                print("❌ --locations argument required for regular script files")
                return
            simon = SimonSaysPaste(args.locations, args.delay)
        else:
            print(f"❌ Recording '{args.script}' not found")
            print("Available recordings:")
            if os.path.exists("recordings"):
                recordings = [d for d in os.listdir("recordings") if os.path.isdir(f"recordings/{d}")]
                if recordings:
                    for recording in sorted(recordings):
                        info_file = f"recordings/{recording}/info.json"
                        if os.path.exists(info_file):
                            with open(info_file, 'r') as f:
                                info = json.load(f)
                            print(f"  📁 {recording} - {info.get('description', 'No description')}")
                        else:
                            print(f"  📁 {recording}")
                else:
                    print("  (no recordings found)")
            else:
                print("  (recordings folder doesn't exist)")
            return
        
        # Execute script file
        if args.countdown:
            # Old countdown method
            print("Starting in 3 seconds...")
            print("Press Ctrl+C to cancel")
            time.sleep(3)
        else:
            # Middle click method
            if not wait_for_middle_click():
                return
            # Don't print anything after middle click - start immediately to avoid focus issues
        
        simon.execute_file(script_file)
    else:
        # Interactive mode
        if not args.locations:
            print("❌ --locations argument required for interactive mode")
            return
            
        simon = SimonSaysPaste(args.locations, args.delay)
        print("\n=== Simon Says Paste Mode ===")
        print("Enter commands (or 'quit' to exit):")
        print("This version uses clipboard for reliable code pasting")
        print("-" * 40)
        
        while True:
            try:
                cmd = input("> ")
                if cmd.lower() in ['quit', 'exit', 'q']:
                    break
                simon.execute_command(cmd)
            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == '__main__':
    main()