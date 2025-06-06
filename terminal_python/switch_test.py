import RPi.GPIO as GPIO
import time

# GPIO pin number (BCM numbering)
SWITCH_PIN = 4

# Setup
GPIO.setmode(GPIO.BCM)       # Use BCM pin numbering
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up

print("Toggle switch test (Press Ctrl+C to exit)")

try:
    while True:
        input_state = GPIO.input(SWITCH_PIN)
        if input_state == GPIO.LOW:
            print("Switch is ON")
        else:
            print("Switch is OFF")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
