# Raspberry Pi detection and GPIO charging-switch access.
import os
import platform

from . import config


class ChargingSwitch:
    def __init__(self) -> None:
        self.is_raspberry_pi = (
            platform.system() == "Linux" and os.uname().machine.startswith("aarch64")
        )
        self.gpio = None
        if self.is_raspberry_pi:
            import RPi.GPIO as GPIO

            self.gpio = GPIO
            self.gpio.setmode(self.gpio.BCM)
            self.gpio.setup(config.SWITCH_PIN, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
            print("Running on Raspberry Pi")
            print(f"Listening for GPIO {config.SWITCH_PIN} (physical pin 7) connected to GND...")

    def read(self) -> int | None:
        return None if self.gpio is None else self.gpio.input(config.SWITCH_PIN)

    def is_charged(self) -> bool:
        return self.read() == self.gpio.LOW if self.gpio is not None else True

    def report_change(self, previous: int | None) -> int | None:
        current = self.read()
        if current is not None and current != previous:
            status = "CONNECTED to GND" if current == self.gpio.LOW else "not connected"
            print(f"GPIO {config.SWITCH_PIN}: {status}", flush=True)
        return current

    def cleanup(self) -> None:
        if self.gpio is not None:
            self.gpio.cleanup()
