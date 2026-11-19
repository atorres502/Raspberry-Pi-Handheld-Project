# Raspberry-Pi-Handheld-Project
Handheld Raspberry Pi Emulator Project code.

## Files
- `controls.py` – reads the joystick and buttons from GPIO. Run it by itself to print which controls are pressed (hardware test).
- `gamepad.py` – turns those controls into a virtual SNES-style gamepad ("Handheld Controller") that emulators can use. It works for NES, SNES, Game Boy, Game Boy Color and Game Boy Advance games.

## Wiring (BCM pin numbers)
Each button goes between its GPIO pin and GND. Pins are set in `controls.py`.

| Control | Pin | | Control | Pin |
|---|---|---|---|---|
| Up | 17 | | A | 5 |
| Down | 27 | | B | 6 |
| Left | 22 | | X | 24 |
| Right | 23 | | Y | 25 |
| Start | 13 | | L (left shoulder) | 26 |
| Select | 19 | | R (right shoulder) | 16 |

Face buttons use the SNES layout: X on top, B on the bottom, Y on the left, A on the right.

## One-time setup on the Pi
```bash
sudo apt install python3-evdev retroarch libretro-nestopia libretro-snes9x libretro-mgba
echo uinput | sudo tee -a /etc/modules
sudo modprobe uinput
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo usermod -aG input $USER
sudo reboot
```
The udev rule and `input` group let `gamepad.py` create the virtual controller without `sudo`, so it runs from Thonny.

If `apt` can't find one of the `libretro-*` cores, install it from inside RetroArch instead: **Main Menu → Online Updater → Core Downloader**.

## Playing games
1. Open `gamepad.py` in Thonny and press Run (F5). Leave it running.
2. Start RetroArch and load a ROM with the matching core:

   | System | Core | Buttons used |
   |---|---|---|
   | NES | Nestopia | D-pad, A, B, Start, Select |
   | SNES | Snes9x | D-pad, A, B, X, Y, L, R, Start, Select |
   | Game Boy / Color / Advance | mGBA | D-pad, A, B, L, R (GBA only), Start, Select |

3. First time only: **Settings → Input → Port 1 Controls → Set All Controls**, press each handheld button when asked, then **Save Controller Profile**. Also set **Hotkey Enable** to Select and **Menu Toggle** to Start, so Select+Start opens the menu (the handheld has no keyboard).

To check the controller without the emulator: `sudo apt install evtest`, run `evtest`, and pick "Handheld Controller".

## Running without Thonny (final build)
Thonny is handy while testing, but it uses memory and has to be started by hand. To start the controller automatically at boot, create `/etc/systemd/system/handheld-gamepad.service`:
```ini
[Unit]
Description=Handheld GPIO gamepad

[Service]
ExecStart=/usr/bin/python3 /home/pi/HandheldPrototyping/gamepad.py
Restart=always

[Install]
WantedBy=multi-user.target
```
Change the path to wherever the repo is on the Pi, then run `sudo systemctl enable --now handheld-gamepad`.
