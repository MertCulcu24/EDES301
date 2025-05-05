import numpy as np
import os
from typing import Any, Dict, List, Tuple, Optional

# Import our modules
from vision_system import VisionSystem
from board_system import BoardSystem

class CalibrationSystem:
    """System for calibrating the board and CNC coordinates"""
    
    def __init__(self, vision: VisionSystem, motor_control: Any, board: BoardSystem):
        """Initialize the calibration system"""
        self.vision = vision
        self.mc = motor_control
        self.board = board
        self.calibration_data = None
    
    def run_calibration(self) -> bool:
        """Run the calibration process"""
        print("Starting system calibration...")
        
        # First, make sure the CNC is homed
        print("Homing CNC first...")
        # Import home_cnc module directly here to avoid circular imports
        import home_cnc as hc
        hc.home_cnc(self.mc)
        
        # Capture the board corners
        print("Capturing board image for calibration...")
        frame = self.vision.capture_frame()
        if frame is None:
            print("Error: Could not capture frame for calibration")
            return False
        
        # Detect the board corners
        corners = self.vision.detect_board(frame)
        if corners is None:
            print("Error: Could not detect board corners for calibration")
            return False
        
        print("Board corners detected in image")
        
        # Now we need to map board corners to CNC coordinates
        print("Please move the CNC to each corner of the board")
        print("Starting with the bottom-left corner (0,0)...")
        
        # Create a list to store the CNC coordinates of each corner
        cnc_corners = []
        
        # Manual calibration process - asking the user to position the CNC
        for i, corner_name in enumerate([
            "bottom-left (0,0)", 
            "bottom-right (7,0)", 
            "top-right (7,7)", 
            "top-left (0,7)"
        ]):
            input(f"Move CNC to {corner_name} corner and press Enter...")
            
            # Get current position
            x, y, _ = self.mc.get_current_position()
            cnc_corners.append((x, y))
            print(f"Recorded position: ({x:.2f}, {y:.2f})")
        
        # Calculate board offset and size based on the CNC coordinates
        # Bottom-left corner is the board offset
        self.board.board_offset_x = cnc_corners[0][0]
        self.board.board_offset_y = cnc_corners[0][1]
        
        # Calculate board size from the distance between corners
        width = abs(cnc_corners[1][0] - cnc_corners[0][0])
        height = abs(cnc_corners[3][1] - cnc_corners[0][1])
        
        # Update board dimensions
        self.board.board_size_mm = (width + height) / 2  # Average for slight discrepancies
        self.board.square_size_mm = self.board.board_size_mm / self.board.squares
        
        print(f"Calibration complete:")
        print(f"Board offset: ({self.board.board_offset_x:.2f}, {self.board.board_offset_y:.2f}) mm")
        print(f"Board size: {self.board.board_size_mm:.2f} mm")
        print(f"Square size: {self.board.square_size_mm:.2f} mm")
        
        # Store calibration data
        self.calibration_data = {
            'board_offset_x': self.board.board_offset_x,
            'board_offset_y': self.board.board_offset_y,
            'board_size_mm': self.board.board_size_mm,
            'image_corners': corners.tolist(),
            'cnc_corners': cnc_corners
        }
        
        return True
    
    def save_calibration(self) -> None:
        """Save calibration data to a file"""
        if self.calibration_data:
            np.savez('calibration_data.npz', **self.calibration_data)
            print("Calibration data saved to calibration_data.npz")
    
    def load_calibration(self) -> bool:
        """Load calibration data from a file"""
        try:
            data = np.load('calibration_data.npz')
            
            # Apply loaded calibration to the board system
            self.board.board_offset_x = float(data['board_offset_x'])
            self.board.board_offset_y = float(data['board_offset_y'])
            self.board.board_size_mm = float(data['board_size_mm'])
            self.board.square_size_mm = self.board.board_size_mm / self.board.squares
            
            # Set the vision system's board corners
            self.vision.board_corners = np.array(data['image_corners'])
            
            # Store all the data
            self.calibration_data = {k: data[k] for k in data.files}
            
            print("Calibration data loaded:")
            print(f"Board offset: ({self.board.board_offset_x:.2f}, {self.board.board_offset_y:.2f}) mm")
            print(f"Board size: {self.board.board_size_mm:.2f} mm")
            print(f"Square size: {self.board.square_size_mm:.2f} mm")
            
            return True
        except Exception as e:
            print(f"Error loading calibration data: {e}")
            return False

# Test function for this module - this requires motor_control and home_cnc
def test_calibration_system():
    """Test the calibration system independently"""
    print("Testing calibration system...")
    print("Note: This test requires motor_control and home_cnc modules")
    
    try:
        # Import required modules
        import motor_control as mc
        import home_cnc as hc
        
        # Initialize motor control
        mc.init_motors()
        hc.init_limit_switches()
        mc.set_limit_check_function(lambda limit_name: hc.check_axis_limits().get(limit_name, False))
        
        # Initialize vision system
        vision = VisionSystem()
        if not vision.init_camera():
            print("Failed to initialize camera. Exiting.")
            return
        
        # Initialize board system
        board = BoardSystem()
        
        # Create calibration system
        calibration = CalibrationSystem(vision, mc, board)
        
        while True:
            print("\nCalibration System Test Menu:")
            print("1. Run new calibration")
            print("2. Save calibration")
            print("3. Load existing calibration")
            print("4. Exit")
            
            choice = input("Enter choice (1-4): ")
            
            if choice == "1":
                calibration.run_calibration()
                
            elif choice == "2":
                calibration.save_calibration()
                
            elif choice == "3":
                if os.path.exists("calibration_data.npz"):
                    calibration.load_calibration()
                else:
                    print("No calibration data file found")
                
            elif choice == "4":
                print("Exiting calibration test...")
                break
                
            else:
                print("Invalid choice. Please enter 1-4.")
    
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Make sure motor_control.py and home_cnc.py are in the same directory")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Clean up
        vision.release_camera()
        
        # Clean up motor control if it was initialized
        if 'mc' in locals():
            mc.cleanup()

if __name__ == "__main__":
    test_calibration_system()