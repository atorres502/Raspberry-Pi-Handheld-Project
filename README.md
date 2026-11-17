# Raspberry-Pi-Handheld-Project
Handheld Raspberry Pi Emulator Project code.

## Files
- `controls.py` – reads the joystick and buttons from GPIO. Run it by itself to print which controls are pressed (hardware test).
- `gamepad.py` – turns those controls into a virtual NES gamepad ("Handheld Controller") that emulators can use.

## One-time setup on the Pi
```bash
sudo apt install python3-evdev retroarch libretro-nestopia
echo uinput | sudo tee -a /etc/modules
sudo modprobe uinput
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo usermod -aG input $USER
sudo reboot
```
The udev rule and `input` group let `gamepad.py` create the virtual controller without `sudo`, so it runs from Thonny.

## Playing NES games
1. Open `gamepad.py` in Thonny and press Run (F5). Leave it running.
2. Start RetroArch and load an NES ROM with the Nestopia core.
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
