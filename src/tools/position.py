from Quartz import CGEventMaskBit, CGEventTapCreate, CGEventGetLocation
from Quartz import kCGEventLeftMouseDown, kCGEventRightMouseDown, kCGSessionEventTap
from Quartz import kCGHeadInsertEventTap, CFRunLoopGetCurrent, CFRunLoopRun, CFRunLoopStop
from Quartz import CFMachPortCreateRunLoopSource, CFRunLoopAddSource, kCFRunLoopDefaultMode

def mouse_click_callback(proxy, event_type, event, refcon):
    loc = CGEventGetLocation(event)
    x, y = int(loc.x), int(loc.y)
    
    if event_type == kCGEventLeftMouseDown:
        print(f"Left click at: x={x}, y={y}")
    elif event_type == kCGEventRightMouseDown:
        print(f"Right click at: x={x}, y={y}")
    
    return event

print("Click anywhere on the screen to see coordinates. Press Ctrl+C to stop.")

try:
    mask = (CGEventMaskBit(kCGEventLeftMouseDown) | 
            CGEventMaskBit(kCGEventRightMouseDown))
    
    tap = CGEventTapCreate(
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        0,
        mask,
        mouse_click_callback,
        None
    )
    
    if tap:
        source = CFMachPortCreateRunLoopSource(None, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopDefaultMode)
        CFRunLoopRun()
    else:
        print("Failed to create event tap. You may need to grant accessibility permissions.")
        print("Go to System Preferences > Security & Privacy > Privacy > Accessibility")
        print("and add Terminal or your Python interpreter to the allowed apps.")
        
except KeyboardInterrupt:
    print("\nStopped.")
    CFRunLoopStop(CFRunLoopGetCurrent())
