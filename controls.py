"""
Reads the handheld's physical controls (joystick + A/B buttons) from the
Raspberry Pi's GPIO pins and exposes them as a simple Game Boy style state:
a 4-way d-pad plus A and B.

Hardware is still being decided, so the joystick type is configurable:
  - "digital": an arcade-style stick with 4 microswitches (one GPIO pin each)
  - "analog":  a thumbstick (two potentiometers) read through an MCP3008 ADC,
               since the Pi has no analog inputs of its own

Buttons are wired between a GPIO pin and GND; the Pi's internal pull-up
resistors are used, so no external resistors are needed.

To test: open this file in Thonny on the Pi and press Run (F5). The Shell
will print which controls are pressed. Press Ctrl+C in the Shell to stop.
gpiozero comes preinstalled on Raspberry Pi OS, so nothing extra is needed.
"""

import time

try:
    from gpiozero import Button
except ImportError:
    raise SystemExit(
        "gpiozero not found. In Thonny, go to Run > Configure interpreter and "
        "choose the default Raspberry Pi OS Python (/usr/bin/python3)."
    )

# ---------------------------------------------------------------------------
# Configuration (BCM pin numbers) -- update once the hardware is final
# ---------------------------------------------------------------------------
JOYSTICK_TYPE = "digital"  # "digital" or "analog"

BUTTON_PINS = {
    "a": 5,
    "b": 6,
}

# Used when JOYSTICK_TYPE == "digital"
DPAD_PINS = {
    "up": 17,
    "down": 27,
    "left": 22,
    "right": 23,
}

# Used when JOYSTICK_TYPE == "analog" (MCP3008 channels, over SPI)
ANALOG_X_CHANNEL = 0
ANALOG_Y_CHANNEL = 1
ANALOG_DEADZONE = 0.25    # how far from center (0..0.5) before a direction counts
ANALOG_INVERT_Y = False   # flip if "up" reads as "down" on your stick

BOUNCE_TIME = 0.01        # seconds; filters switch chatter on button presses
POLL_RATE_HZ = 120


class Controls:
    """Reads the current state of every input on the handheld."""

    def __init__(self, joystick_type=JOYSTICK_TYPE):
        self.joystick_type = joystick_type
        self.buttons = {
            name: Button(pin, pull_up=True, bounce_time=BOUNCE_TIME)
            for name, pin in BUTTON_PINS.items()
        }

        if joystick_type == "digital":
            self.dpad = {
                name: Button(pin, pull_up=True, bounce_time=BOUNCE_TIME)
                for name, pin in DPAD_PINS.items()
            }
        elif joystick_type == "analog":
            from gpiozero import MCP3008
            self.axis_x = MCP3008(channel=ANALOG_X_CHANNEL)
            self.axis_y = MCP3008(channel=ANALOG_Y_CHANNEL)
        else:
            raise ValueError(f"Unknown joystick type: {joystick_type!r}")

    def _read_analog_dpad(self):
        # MCP3008 values range 0.0..1.0 with ~0.5 at rest; shift to -0.5..0.5
        x = self.axis_x.value - 0.5
        y = self.axis_y.value - 0.5
        if ANALOG_INVERT_Y:
            y = -y

        directions = {"up": False, "down": False, "left": False, "right": False}
        # Snap to the dominant axis so the stick behaves like a 4-way d-pad
        # (prevents accidental diagonals in grid-based games)
        if max(abs(x), abs(y)) < ANALOG_DEADZONE:
            return directions
        if abs(x) > abs(y):
            directions["right" if x > 0 else "left"] = True
        else:
            directions["up" if y > 0 else "down"] = True
        return directions

    def read(self):
        """Return a dict of every control name -> True if pressed."""
        if self.joystick_type == "digital":
            state = {name: btn.is_pressed for name, btn in self.dpad.items()}
            # Opposite directions can't both be held on a real d-pad
            if state["up"] and state["down"]:
                state["up"] = state["down"] = False
            if state["left"] and state["right"]:
                state["left"] = state["right"] = False
        else:
            state = self._read_analog_dpad()

        for name, btn in self.buttons.items():
            state[name] = btn.is_pressed
        return state

    def close(self):
        """Release the GPIO pins."""
        devices = list(self.buttons.values())
        if self.joystick_type == "digital":
            devices += list(self.dpad.values())
        else:
            devices += [self.axis_x, self.axis_y]
        for device in devices:
            device.close()


def main():
    controls = Controls()
    previous = None
    print(f"Reading controls ({controls.joystick_type} joystick). Ctrl+C to quit.")
    try:
        while True:
            state = controls.read()
            if state != previous:
                pressed = [name for name, down in state.items() if down]
                print("Pressed:", ", ".join(pressed) if pressed else "(none)")
                previous = state
            time.sleep(1 / POLL_RATE_HZ)
    except KeyboardInterrupt:
        pass
    finally:
        controls.close()


if __name__ == "__main__":
    main()
