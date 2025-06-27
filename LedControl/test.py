#!/usr/bin/env python3
import board
import neopixel
import time

# Configure NeoPixel settings
NUM_PIXELS = 28  # Change this to match your number of LEDs
BRIGHTNESS = 0.2  # Set brightness (0.0 to 1.0)
GPIO_PIN = board.D18  # GPIO 18

# Initialize the NeoPixel strip
pixels = neopixel.NeoPixel(
    GPIO_PIN,
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,  # Only send data to LEDs when we say
    pixel_order=neopixel.GRB  # Common LED color order
)

def clear_pixels():
    """Turn off all pixels"""
    pixels.fill((0, 0, 0))
    pixels.show()

def simple_demo():
    """Run a simple color demonstration"""
    try:
        print("Running NeoPixel demo. Press Ctrl+C to stop.")
        
        while True:
            # Red
            pixels.fill((255, 0, 0))
            pixels.show()
            time.sleep(1)
            
            # Green
            pixels.fill((0, 255, 0))
            pixels.show()
            time.sleep(1)
            
            # Blue
            pixels.fill((0, 0, 255))
            pixels.show()
            time.sleep(1)
            
    except KeyboardInterrupt:
        clear_pixels()
        print("\nDemo stopped. All pixels turned off.")

if __name__ == "__main__":
    clear_pixels()  # Start with all LEDs off
    simple_demo()
