# ClawMind 🦾

**A hands-free robotic claw machine controlled entirely by head movements — built for accessibility at StarkHacks 2026, Purdue University.**

ClawMind allows anyone, including people with limited hand mobility, to control a physical robotic claw using only their face. No hands required.

---

## Demo

[![ClawMind Demo](https://img.youtube.com/vi/r2palXzuYOI/0.jpg)](https://youtu.be/r2palXzuYOI)

> Tilt your head. Move the claw. Open your mouth. Grab.

---

## How It Works

A laptop webcam tracks your face in real time using MediaPipe FaceMesh (478 facial landmarks). Head gestures are converted into movement commands that travel over WiFi to a Raspberry Pi, which forwards them to an Arduino Nano controlling the motors.

### Control Scheme

| Gesture | Action |
|---|---|
| Tilt head left | Move claw left |
| Tilt head right | Move claw right |
| Look up | Move claw forward |
| Look down | Move claw back |
| Open mouth | Trigger grab sequence |

### Grab Sequence (automatic)
1. Z axis motor lowers the claw
2. Servo closes and grabs the object
3. Z axis motor retracts back up

---

## System Architecture

```
Laptop (webcam)
    ↓ MediaPipe FaceMesh — detects head tilt, nod, mouth
face_control.py — converts gestures to commands
    ↓ writes to /tmp/claw_command.txt
cmd_sender.py — reads file, HTTP POSTs to Pi
    ↓ WiFi (HTTP POST)
Raspberry Pi 4 — bridge.py HTTP server (port 8888)
    ↓ USB serial (9600 baud)
Arduino Nano — motor control firmware
    ↓
L298N driver → TT DC motors (X and Z axis)
A4988 driver → Stepper motor (Y axis)
MG90S Servo → Claw grip
```

---

## Tech Stack

- **Computer Vision:** Python, MediaPipe FaceMesh, OpenCV, NumPy
- **Communication:** HTTP over WiFi (laptop → Pi), USB Serial (Pi → Arduino)
- **Hardware:** Raspberry Pi 4, Arduino Nano, L298N motor driver, A4988 stepper driver, MG90S servo, TT DC motors
- **Cloud:** Viam robotics platform (viam-server on Pi, registered on app.viam.com)
- **Mechanical:** Custom 3D printed gantry frame (STEP + STL files in `/cad`)

---

## Project Structure

```
ClawMind/
├── README.md
├── Code/
│   ├── laptop/
│   │   ├── face_control.py
│   │   └── cmd_sender.py
│   ├── pi/
│   │   └── bridge.py
│   └── arduino/
│       └── Arduino.ino
├── cad/
│   └── *.step / *.stl
└── schematics/
    ├── stepper_wiring.jpg
    └── dc_motor_wiring.jpg
```

---

## Setup & Installation

### Laptop
```bash
# Create virtual environment for mediapipe
python3.11 -m venv ~/venv_mediapipe
source ~/venv_mediapipe/bin/activate
pip install mediapipe==0.10.9 opencv-python numpy

# Run face control
python face_control.py
```

```bash
# In a second terminal — send commands to Pi
python3 cmd_sender.py
```

### Raspberry Pi
```bash
pip3 install pyserial --break-system-packages
python3 bridge.py
```

### Arduino
Open `ClawMind.ino` in Arduino IDE, select **Arduino Nano** board and the correct port, then upload.

---

## Key Technical Challenges

**Protobuf version conflict** — MediaPipe and Viam SDK required incompatible versions of protobuf. Solved by running them in separate Python virtual environments communicating through a shared local file.

**Nod detection accuracy** — Early versions incorrectly triggered forward/back commands when the user turned their head sideways. Fixed by measuring the nose's vertical position relative to the ear midpoint instead of the nose-to-chin angle.

**3.3V vs 5V logic** — Arduino UNO Q's 3.3V GPIO couldn't reliably drive the L298N and A4988 motor drivers. Switched to Arduino Nano (5V logic) to resolve motor control issues.

---

## The Team

| Name | Role |
|---|---|
| **Kshitij Kesharwani** | Software & Systems — CV pipeline, gesture detection, Raspberry Pi setup, HTTP relay, system architecture |
| **Duna Areny Molne** | Electrical Engineering — motor drivers, Arduino firmware, circuit design, wiring, hardware debugging |
| **Younji Kim** | Mechanical Engineering — CAD design, 3D printing, physical assembly, gantry frame |

---

## Inspiration

The idea was born from Younji's vision of creating something interactive and fun — a project that makes computer vision tangible for people encountering it for the first time. We pushed the concept further by designing it for accessibility: what if someone with limited hand mobility could play a claw machine too?

---

## Built At

**StarkHacks 2026** — Hardware Hackathon at Purdue University
**Table 36**

---

*Built with ❤️ and way too little sleep.*
