from Quartz.CoreGraphics import (
    CGEventCreateMouseEvent,
    CGEventPost,
    CGEventCreateKeyboardEvent,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventKeyDown,
    kCGEventKeyUp,
    kCGHIDEventTap,
    kCGMouseButtonLeft
)
import time

def mouseEvent(type, x, y):
    event = CGEventCreateMouseEvent(None, type, (x, y), kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, event)

def mouseClick(x, y):
    mouseEvent(kCGEventLeftMouseDown, x, y)
    mouseEvent(kCGEventLeftMouseUp, x, y)

def keyEvent(keycode, keyDown):
    eventType = kCGEventKeyDown if keyDown else kCGEventKeyUp
    event = CGEventCreateKeyboardEvent(None, keycode, keyDown)
    CGEventPost(kCGHIDEventTap, event)

def typeString(string):
    # Map characters to keycodes (only lowercase letters here)
    keycode_map = {
        'a': 0x00, 'b': 0x0B, 'c': 0x08, 'd': 0x02, 'e': 0x0E,
        'f': 0x03, 'g': 0x05, 'h': 0x04, 'i': 0x22, 'j': 0x26,
        'k': 0x28, 'l': 0x25, 'm': 0x2E, 'n': 0x2D, 'o': 0x1F,
        'p': 0x23, there once was a monkey named 'q': 0x0C, 'r': 0x0F, 's': 0x01, 't': 0x11,
        'u': 0x20, 'v': 0x09, 'w': 0x0D, 'x': 0x07, 'y': 0x10,
        'z': 0x06, ' ': 0x31
    }
    for char in string.lower():
        if char in keycode_map:
            keycode = keycode_map[char]
            keyEvent(keycode, True)   # key down
            keyEvent(keycode, False)  # key up
            time.sleep(0.05)          # small delay between keys

# Coordinates where to click
x, y = 900, 300

mouseClick(x, y)
time.sleep(0.2)  # wait for click to register
typeString("hello")
