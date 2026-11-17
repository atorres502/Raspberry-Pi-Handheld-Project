"""
Turns the handheld's GPIO controls into a virtual NES gamepad that emulators
(RetroArch, RetroPie, etc.) see exactly like a USB controller.

It reuses Controls from controls.py to read the pins, then forwards every
press/release to Linux through the kernel's uinput module.

To use: run this file in Thonny (F5) and leave it running, then start the
emulator. See README.md for the one-time setup (python3-evdev + uinput
permissions). Press Ctrl+C in the Shell to stop.
"""

import time

from controls import Controls, POLL_RATE_HZ

try:
    from evdev import UInput, ecodes
except ImportError:
    raise SystemExit(
        "evdev not found. Install it with:  sudo apt install python3-evdev\n"
        "Then in Thonny use Run > Configure interpreter and choose the default "
        "Raspberry Pi OS Python (/usr/bin/python3)."
    )

DEVICE_NAME = "Handheld Controller"

# Control name (from Controls.read()) -> Linux gamepad button code.
# Uses the standard layout: BTN_EAST is the right face button (NES A),
# BTN_SOUTH the bottom one (NES B).
BUTTON_CODES = {
    "up": ecodes.BTN_DPAD_UP,
    "down": ecodes.BTN_DPAD_DOWN,
    "left": ecodes.BTN_DPAD_LEFT,
    "right": ecodes.BTN_DPAD_RIGHT,
    "a": ecodes.BTN_EAST,
    "b": ecodes.BTN_SOUTH,
    "start": ecodes.BTN_START,
    "select": ecodes.BTN_SELECT,
}


def open_virtual_gamepad():
    try:
        return UInput(
            {ecodes.EV_KEY: list(BUTTON_CODES.values())},
            name=DEVICE_NAME,
        )
    except (PermissionError, OSError) as error:
        raise SystemExit(
            f"Could not create the virtual gamepad ({error}).\n"
            "Make sure the uinput module is loaded and your user can write to "
            "/dev/uinput -- see the setup steps in README.md (then reboot)."
        )


def main():
    controls = Controls()
    gamepad = open_virtual_gamepad()
    previous = {name: False for name in BUTTON_CODES}
    print(f'Virtual gamepad "{DEVICE_NAME}" ready. Start the emulator. '
          "Ctrl+C to quit.")
    try:
        while True:
            state = controls.read()
            changed = False
            for name, code in BUTTON_CODES.items():
                pressed = state.get(name, False)
                if pressed != previous[name]:
                    gamepad.write(ecodes.EV_KEY, code, 1 if pressed else 0)
                    previous[name] = pressed
                    changed = True
            if changed:
                gamepad.syn()
            time.sleep(1 / POLL_RATE_HZ)
    except KeyboardInterrupt:
        pass
    finally:
        gamepad.close()
        controls.close()


if __name__ == "__main__":
    main()
