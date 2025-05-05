import os
import time
from typing import Tuple, Dict, Optional

# Import our modules
import motor_control as mc
import home_cnc as hc
from vision_system import VisionSystem
from board_system import BoardSystem
from calibration_system import CalibrationSystem

class CNCCheckersSystem:
    """
    Main class for the CNC Checkers system
    Integrates all components and provides the user interface
    """

    def __init__(self, board_size_mm=200, squares=8):
        print("Initializing CNC Checkers system...")

        # Initialize the motor control subsystem
        mc.init_motors()

        # Initialize limit switches and home the system
        hc.init_limit_switches()
        mc.set_limit_check_function(self.check_limit)
        hc.home_cnc(mc)

        # Record Z limits after homing
        self.Z_MIN, self.Z_MAX = hc.get_z_limits(mc)
        self.Z_ATTACH = self.Z_MAX - 2.0
        self.Z_PLACE = self.Z_MIN + 2.0
        self.HOME_POSITION = mc.get_current_position()

        # Initialize the board coordinate system
        self.board = BoardSystem(board_size_mm, squares)

        # Initialize the vision system
        self.vision = VisionSystem()
        if not self.vision.init_camera():
            print("Warning: Failed to initialize camera. Some features will be disabled.")

        # Initialize the calibration system
        self.calibration = CalibrationSystem(self.vision, mc, self.board)

        # Try to load existing calibration
        if os.path.exists("calibration_data.npz"):
            self.calibration.load_calibration()

    def check_limit(self, limit_name):
        """Check a specific limit switch"""
        limits = hc.check_axis_limits()
        return limits.get(limit_name, False)

    def cleanup(self):
        """Clean up resources when shutting down"""
        print("Cleaning up resources...")
        self.vision.release_camera()
        mc.cleanup()

    def move_piece(self, start_square, end_square):
        """Move a checker piece from start_square to end_square"""
        if not (self.board.is_valid_square(*start_square) and 
                self.board.is_valid_square(*end_square)):
            print("Error: Invalid square coordinates")
            return False

        # Convert board squares to CNC coordinates
        start_x, start_y = self.board.board_to_cnc(*start_square)
        end_x, end_y = self.board.board_to_cnc(*end_square)

        z_attach = self.Z_ATTACH
        z_place = self.Z_PLACE
        home_x, home_y, home_z = self.HOME_POSITION

        print(f"Moving piece from {start_square} to {end_square}")

        # Step 1: Move to piece location (XY first)
        mc.move_to_position(start_x, start_y, self.Z_MIN)

        # Step 2: Raise Z to attach the piece
        mc.move_z(z_attach)
        time.sleep(0.3)

        # Step 3: Move to destination (Z stays high)
        mc.move_to_position(end_x, end_y, z_attach)

        # Step 4: Lower Z to place the piece
        mc.move_z(z_place)
        time.sleep(0.3)

        # Step 5: Return to home
        mc.move_to_position(home_x, home_y, self.Z_MIN)
        return True

    def run(self):
        """Run the main interface loop"""
        while True:
            print("\n=== CNC Checkers Menu ===")
            print("1. Scan board")
            print("2. Move piece")
            print("3. Calibrate system")
            print("4. Exit")

            choice = input("Enter your choice (1-4): ")

            if choice == "1":
                pieces = self.vision.scan_board()
                if pieces:
                    self.vision.print_board_state(pieces)

            elif choice == "2":
                try:
                    x1 = int(input("Enter start X (0–7): "))
                    y1 = int(input("Enter start Y (0–7): "))
                    x2 = int(input("Enter end X (0–7): "))
                    y2 = int(input("Enter end Y (0–7): "))
                    self.move_piece((x1, y1), (x2, y2))
                except ValueError:
                    print("Invalid input. Use numbers between 0–7.")

            elif choice == "3":
                if self.calibration.run_calibration():
                    self.calibration.save_calibration()

            elif choice == "4":
                print("Exiting CNC Checkers.")
                self.cleanup()
                break

            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    system = CNCCheckersSystem()
    system.run()
