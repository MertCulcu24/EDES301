# CNC Checkers System

This project implements a CNC-controlled checkers board system that uses a magnetic mechanism underneath the board to move checker pieces. The system includes computer vision for piece detection and a full control interface.

## System Components

1. **Motor Control Module** (`motor_control.py`): Controls the X, Y, and Z axes of the CNC machine
2. **Home CNC Module** (`home_cnc.py`): Handles homing procedures using limit switches
3. **Vision System** (`vision_system.py`): Handles camera input and piece detection
4. **Board System** (`board_system.py`): Manages coordinate conversions between board and CNC positions
5. **Calibration System** (`calibration_system.py`): Aligns the camera view with the physical CNC coordinate system
6. **Main CNC Checkers System** (`cnc_checkers_system.py`): Integrates all components and provides the user interface
7. **Test Integration** (`test_integration.py`): Provides a testing framework for each component

## Prerequisites

- Python 3.6 or higher
- BeagleBone Black or similar board with GPIO support
- Adafruit_BBIO library (`pip install Adafruit_BBIO`)
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)
- USB camera

## Implementation Steps

Follow these steps to implement and test the system incrementally:

### Step 1: Motor Control and Homing

You already have working implementations of `motor_control.py` and `home_cnc.py`. These provide the foundation for controlling the CNC machine.

Test these components using:
```
python test_integration.py
```
And select option 6 to test the calibration system. You'll need both the camera and CNC system working for this step.

### Step 5: Piece Movement

Test the piece movement functionality to ensure the CNC can effectively move pieces on the board:

```
python test_integration.py
```

And select option 7 to test piece movement. This will guide you through moving a piece from one square to another.

### Step 6: Full System Integration

Once all individual components are working, you can integrate them into the full system:

```
python cnc_checkers_system.py
```

This will run the complete CNC Checkers system with all components integrated.

## Usage Instructions

### Calibration

Before using the system, you'll need to calibrate it:

1. Start the system (`python cnc_checkers_system.py`)
2. Select option 4 from the menu ("Calibrate system")
3. Follow the prompts to position the CNC at each corner of the board
4. The system will calculate the board position and dimensions

### Moving Pieces

To move a checker piece:

1. Select option 2 from the main menu ("Move piece")
2. Enter the starting square coordinates (X, Y) where the piece is located
3. Enter the destination square coordinates (X, Y)
4. The system will:
   - Move to the starting position
   - Raise the magnet to attach to the piece
   - Move to the destination
   - Lower the magnet to release the piece

### Scanning the Board

To scan the board and detect pieces:

1. Select option 1 from the main menu ("Scan board")
2. The system will capture an image from the camera and detect all pieces
3. The board state will be displayed both graphically and as text

### Auto-Play

The system includes a simple demo feature to automatically make a move:

1. Select option 7 from the main menu ("Auto-play move")
2. The system will scan the board, find a piece, and move it to a valid adjacent square

## Troubleshooting

- **Camera Not Detected**: Ensure your USB camera is connected and recognized by the system
- **Limit Switch Issues**: Check the wiring of your limit switches and their configuration in `home_cnc.py`
- **Movement Problems**: Verify the motor control settings in `motor_control.py`
- **Board Detection Failures**: Adjust the board detection parameters in `vision_system.py`
- **Calibration Issues**: Make sure the lighting is good for the camera and there's clear contrast between the board and background

## Extending the System

You can extend this system in several ways:

1. **Game Logic**: Add checkers game rules to validate moves
2. **AI Player**: Implement an AI to play against a human player
3. **Multiple Games**: Extend the system to support other board games like chess
4. **User Interface**: Create a graphical user interface for easier interaction

## File Structure

```
CNC_Checkers/
│
├── motor_control.py        # CNC motor control module
├── home_cnc.py             # CNC homing functionality
├── vision_system.py        # Camera and piece detection
├── board_system.py         # Board coordinate system
├── calibration_system.py   # System calibration
├── cnc_checkers_system.py  # Main system interface
└── test_integration.py     # Testing framework
```s 1, 2, and 3 to test motor control, limit switches, and homing.

### Step 2: Board System

The board system (`board_system.py`) manages coordinate conversions between the checkers board and the CNC machine. This component doesn't have hardware dependencies, so you can implement and test it independently.

Test with:
```
python board_system.py
```

### Step 3: Vision System

The vision system (`vision_system.py`) handles camera input and piece detection. You can implement and test this component next:

Test with:
```
python vision_system.py
```

Make sure your USB camera is connected. This test will check camera access, board detection, and piece recognition.

### Step 4: Calibration System

The calibration system (`calibration_system.py`) aligns the camera view with the physical CNC coordinate system. This component depends on the vision system, board system, and motor control.

Test with:
```
python test_integration.py
```
And select option