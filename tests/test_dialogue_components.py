# Tests the refactored dialogue components without launching the Pygame UI.
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from terminal_python import config, inactivity, message_store, theme


class InactivityControllerTests(unittest.TestCase):
    def test_sleeping_prompt_never_enters_confirmation(self):
        controller = inactivity.InactivityController(last_input_time=0)

        result = controller.update(current_prompt=0, now=config.IDLE_TIMEOUT + 1)

        self.assertIsNone(result)
        self.assertFalse(controller.confirmation_active)
        self.assertEqual(controller.last_input_time, config.IDLE_TIMEOUT + 1)

    def test_confirmation_can_be_accepted_or_expire(self):
        controller = inactivity.InactivityController(last_input_time=0)

        self.assertEqual(controller.update(1, config.IDLE_TIMEOUT + 1), "confirm")
        self.assertTrue(controller.confirmation_active)
        self.assertEqual(controller.seconds_remaining(config.IDLE_TIMEOUT + 1), config.CONFIRMATION_TIMEOUT + 1)

        controller.confirm_presence(config.IDLE_TIMEOUT + 2)
        self.assertFalse(controller.confirmation_active)
        self.assertIsNone(controller.update(1, config.IDLE_TIMEOUT + config.CONFIRMATION_TIMEOUT + 3))

        controller = inactivity.InactivityController(last_input_time=0)
        controller.update(1, config.IDLE_TIMEOUT + 1)
        self.assertEqual(
            controller.update(1, config.IDLE_TIMEOUT + config.CONFIRMATION_TIMEOUT + 1),
            "restart",
        )

    def test_alert_has_two_pulses(self):
        controller = inactivity.InactivityController(last_input_time=0)
        start = config.IDLE_TIMEOUT + 1
        controller.update(1, start)

        self.assertAlmostEqual(controller.pulse_amount(start), 0.0)
        self.assertAlmostEqual(controller.pulse_amount(start + 1), 1.0)
        self.assertAlmostEqual(controller.pulse_amount(start + 2), 0.0)
        self.assertAlmostEqual(controller.pulse_amount(start + 3), 1.0)
        self.assertAlmostEqual(controller.pulse_amount(start + 4), 0.0)


class ComponentTests(unittest.TestCase):
    def test_blend_colors_interpolates_rgb(self):
        result = theme.blend_colors(theme.BACKGROUND, theme.TEXT, 0.5)
        self.assertEqual(result, (130, 144, 4, 255))

    def test_append_message_atomically_updates_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "messages.json"
            with patch("terminal_python.message_store.time.strftime", return_value="23-10-2026 12:00:00"):
                result = message_store.append_message(path, "Ada", "Hello")

            self.assertEqual(result["name"], "Ada")
            self.assertEqual(json.loads(path.read_text())[0]["message"], "Hello")
            self.assertFalse(path.with_name("messages.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
