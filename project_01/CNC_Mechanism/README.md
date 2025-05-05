Smart Checkers Mechanism

A fully automated checkers-playing mechanism built with CNC hardware, a PocketBeagle board, and computer vision. This project uses a magnetic pickup system to move pieces across a physical board by interpreting square coordinates and translating them into precise CNC movements.

---
Project Structure
```
Smart Checkers Mechanism
├── cnc_server.py             # TCP server running on PocketBeagle to handle commands
├── motor_control.py         # Low-level stepper motor movement and homing logic
├── remote_motor_control.py  # Windows-side client to send CNC commands over TCP
├── home_cnc.py              # Calls homing routines for all axes (X, Y, Z)
├── calibration_system.py    # Vision-only board calibration using corner detection
├── vision_system.py         # OpenCV-based board and piece detection
├── cnc_checkers.py          # Main interface for playing the game (move pieces, calibrate, etc.)
├── board_system.py          # Handles board square to CNC position mapping
└── README.md                # This file
```

---

Hardware Overview

* **PocketBeagle** – microcontroller for real-time CNC control
* **CNC Shield** – connects stepper drivers to PocketBeagle
* **Stepper Motors (X, Y, Z)** – drives the magnet to pick and place checkers
* **Limit Switches (min/max)** – for homing and movement constraints
* **Webcam** – detects board layout and piece positions
* **Laser-Cut Board** – checkers board mounted above mechanism
* **Neodymium Magnet (Z-axis)** – attaches from below to move magnetic checkers pieces

---

## Software Features

### Homing & Initialization (`home_cnc.py`)

* Each axis homes to both min and max limit switches
* System calculates travel range and centers to a known position
* After homing, the position is reset to (0, 0, 0)

### Board Calibration (`calibration_system.py`)

* Uses vision system to detect board corners
* Combines known physical board size with CNC travel limits
* Automatically maps (x, y) board squares to CNC mm positions

### Vision System (`vision_system.py`)

* Uses OpenCV to:

  * Detect board corners
  * Warp and align camera view
  * Detect black pieces using HSV color thresholds
* Can be tested independently with `scan_board()` function

### CNC Communication (`cnc_server.py` + `remote_motor_control.py`)

* Sends and receives commands like:

  * `MOVE startX startY endX endY`
  * `JOG_TO x_mm y_mm z_mm`
  * `GET_Z_LIMITS`
* Position and limit updates are tracked on both ends

### Piece Movement (`cnc_checkers.py`)

* Lets user input a start and destination square
* The magnet lifts from below, moves across the board, and releases the piece
* Movement avoids existing pieces if needed (partially implemented)

---

## How to Run

1. **Start the CNC server on the PocketBeagle**:

   ```bash
   python3 cnc_server.py
   ```

2. **From your PC, run the client menu**:

   ```bash
   python remote_motor_control.py
   ```

3. **Commands available**:

   * Homing
   * Calibration
   * Move a piece
   * View camera and scan board

---

## Known Issues

* Sometimes false limits are triggered due to electrical noise → use debounce
* Vision system may misdetect pieces in low lighting
* Y-axis direction required inversion due to mechanical configuration
* Homing must complete successfully before sending any move commands

---

## Future Work

* Add full multi-piece path planning with collision avoidance
* Improve Z-axis control to dynamically vary pickup height
* Use ArUco markers or chessboard pattern for more robust calibration
* Integrate GUI for easier interaction

---

## Author

**Mert Culcu**
EDES 301 Final Project – Smart Checkers Mechanism

---
