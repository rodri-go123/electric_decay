# Manages inactivity detection, confirmation countdowns, and alert pulses.
import time
from dataclasses import dataclass

from . import config


@dataclass
class InactivityController:
    last_input_time: float
    confirmation_deadline: float | None = None
    alert_started: float | None = None
    next_alert: float | None = None
    confirmation_active: bool = False

    @classmethod
    def create(cls) -> "InactivityController":
        return cls(last_input_time=time.time())

    def register_input(self, now: float | None = None) -> None:
        self.last_input_time = time.time() if now is None else now

    def update(self, current_prompt: int, now: float | None = None) -> str | None:
        now = time.time() if now is None else now
        if current_prompt == 0:
            self.last_input_time = now
            return None
        if self.confirmation_active:
            if now >= self.confirmation_deadline:
                self.reset(now)
                return "restart"
            return None
        if now - self.last_input_time > config.IDLE_TIMEOUT:
            self.confirmation_active = True
            self.confirmation_deadline = now + config.CONFIRMATION_TIMEOUT
            self.alert_started = now
            self.next_alert = now + config.CONFIRMATION_ALERT_INTERVAL
            return "confirm"
        return None

    def confirm_presence(self, now: float | None = None) -> None:
        self.confirmation_active = False
        self.confirmation_deadline = None
        self.alert_started = None
        self.next_alert = None
        self.register_input(now)

    def reset(self, now: float | None = None) -> None:
        self.confirmation_active = False
        self.confirmation_deadline = None
        self.alert_started = None
        self.next_alert = None
        self.register_input(now)

    def seconds_remaining(self, now: float | None = None) -> int:
        now = time.time() if now is None else now
        if self.confirmation_deadline is None:
            return 0
        return max(0, int(self.confirmation_deadline - now) + 1)

    def pulse_amount(self, now: float | None = None) -> float:
        now = time.time() if now is None else now
        if self.alert_started is None:
            return 0.0
        if self.next_alert is not None and now >= self.next_alert:
            self.alert_started = now
            self.next_alert += config.CONFIRMATION_ALERT_INTERVAL
        elapsed = now - self.alert_started
        if not 0 <= elapsed < config.CONFIRMATION_ALERT_DURATION or elapsed >= 4.0:
            return 0.0
        progress = (elapsed % 2.0) / 2.0
        return 1 - abs(2 * progress - 1)
