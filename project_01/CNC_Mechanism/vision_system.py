import cv2
import numpy as np
import time
from typing import Tuple, List, Dict, Optional

class VisionSystem:
    """
    Vision system to detect checker pieces on the board
    """
    
    def __init__(self):
        """Initialize the vision system"""
        self.cap = None
        self.calibration_data = None
        self.board_corners = None
        self.squares = 8  # Standard checkers board size
    
    def init_camera(self) -> bool:
        """Initialize the camera"""
        try:
            self.cap = cv2.VideoCapture(2)  # Use the default camera
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
                
            # Set camera resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            print("Camera initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def release_camera(self) -> None:
        """Release the camera resources"""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            print("Camera released")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from the camera"""
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                print("Error: Failed to capture frame")
        else:
            print("Error: Camera not initialized")
        return None
    
    def detect_board(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect the checkerboard in the frame
        Returns the corners of the board if found
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to highlight the board
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest contour (presumably the board)
        if contours:
            board_contour = max(contours, key=cv2.contourArea)
            
            # Approximate the contour to find corners
            epsilon = 0.02 * cv2.arcLength(board_contour, True)
            approx = cv2.approxPolyDP(board_contour, epsilon, True)
            
            # If we have four corners, we've likely found the board
            if len(approx) == 4:
                # Sort corners to get a consistent order: top-left, top-right, bottom-right, bottom-left
                corners = np.array([p[0] for p in approx], dtype="float32")
                rect = self.order_points(corners)
                self.board_corners = rect
                return rect
                
        print("Error: Could not detect board corners")
        return None
    
    def order_points(self, pts: np.ndarray) -> np.ndarray:
        """
        Order points in top-left, top-right, bottom-right, bottom-left order
        """
        # Sort by sum of coordinates (x+y)
        # The top-left point will have the smallest sum
        # The bottom-right point will have the largest sum
        s = pts.sum(axis=1)
        rect = np.zeros((4, 2), dtype="float32")
        rect[0] = pts[np.argmin(s)]  # Top-left
        rect[2] = pts[np.argmax(s)]  # Bottom-right
        
        # Sort by difference of coordinates (x-y)
        # The top-right point will have the largest difference
        # The bottom-left point will have the smallest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmax(diff)]  # Top-right
        rect[3] = pts[np.argmin(diff)]  # Bottom-left
        
        return rect
    
    def detect_pieces(self, frame: np.ndarray) -> Dict[Tuple[int, int], str]:
        """
        Detect checker pieces on the board
        Returns a dictionary mapping board coordinates to piece types ('R', 'B', or None)
        """
        if self.board_corners is None:
            self.detect_board(frame)
            if self.board_corners is None:
                print("Error: Board corners not detected")
                return {}
        
        # Create perspective transform to get a bird's eye view
        width = 800
        height = 800
        dst = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")
        M = cv2.getPerspectiveTransform(self.board_corners, dst)
        warped = cv2.warpPerspective(frame, M, (width, height))
        
        # Create a dictionary to store piece locations
        pieces = {}
        square_size = width // self.squares
        
        # Process each square on the board
        for row in range(self.squares):
            for col in range(self.squares):
                # Calculate square boundaries
                x = col * square_size
                y = row * square_size
                
                # Extract the square
                square = warped[y:y+square_size, x:x+square_size]
                
                # Check if a piece is present in this square
                piece_type = self.identify_piece(square)
                if piece_type:
                    pieces[(col, row)] = piece_type
        
        return pieces
    
    def identify_piece(self, square: np.ndarray) -> Optional[str]:
        """
        Identify if the square contains a piece and determine its type
        Returns 'R' for red pieces, 'B' for black pieces, or None if no piece
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(square, cv2.COLOR_BGR2HSV)
        
        # Calculate the average color in the center of the square
        center_region = square[square.shape[0]//4:3*square.shape[0]//4, 
                               square.shape[1]//4:3*square.shape[1]//4]
        
        # Check if there's significant color (piece) in the center
        avg_color = np.mean(center_region, axis=(0, 1))
        
        # Check brightness (V in HSV) to see if there's a piece
        # Pieces should have different brightness than empty squares
        if avg_color[2] < 80:  # Dark piece (black)
            return 'B'
        elif 150 < avg_color[0] < 180:  # Red piece (checking Hue)
            return 'R'
        
        # No piece detected
        return None
    
    def scan_board(self) -> Dict[Tuple[int, int], str]:
        """Scan the board and detect all pieces"""
        frame = self.capture_frame()
        if frame is None:
            return {}
            
        # Detect the board corners
        if self.board_corners is None:
            self.detect_board(frame)
            if self.board_corners is None:
                return {}
        
        # Detect pieces
        pieces = self.detect_pieces(frame)
        
        # Display the result
        self.display_board_state(pieces, frame)
        
        return pieces
    
    def print_board_state(self, pieces: Dict[Tuple[int, int], str]) -> None:
        """Print a text representation of the board state"""
        print("\nCurrent Board State:")
        print("  0 1 2 3 4 5 6 7")
        print(" +-+-+-+-+-+-+-+-+")
        
        for row in range(8):
            print(f"{row}|", end="")
            for col in range(8):
                piece = pieces.get((col, row), " ")
                print(f"{piece}|", end="")
            print("\n +-+-+-+-+-+-+-+-+")
    
    def display_board_state(self, pieces: Dict[Tuple[int, int], str], frame: Optional[np.ndarray] = None) -> None:
        """Display a visual representation of the board state"""
        if frame is None:
            frame = self.capture_frame()
            if frame is None:
                return
        
        # Draw the detected board corners
        if self.board_corners is not None:
            for corner in self.board_corners:
                cv2.circle(frame, (int(corner[0]), int(corner[1])), 5, (0, 255, 0), -1)
            
            # Draw board grid
            width = 800
            height = 800
            dst = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")
            M = cv2.getPerspectiveTransform(self.board_corners, dst)
            warped = cv2.warpPerspective(frame, M, (width, height))
            
            # Create a visualization of the board with detected pieces
            board_viz = np.zeros((width, height, 3), dtype=np.uint8)
            square_size = width // 8
            
            # Draw the checkerboard pattern
            for row in range(8):
                for col in range(8):
                    x = col * square_size
                    y = row * square_size
                    
                    # Alternating pattern for squares
                    color = (200, 200, 200) if (row + col) % 2 == 0 else (50, 50, 50)
                    cv2.rectangle(board_viz, (x, y), (x + square_size, y + square_size), color, -1)
                    
                    # Draw pieces
                    if (col, row) in pieces:
                        piece_color = (0, 0, 255) if pieces[(col, row)] == 'R' else (0, 0, 0)
                        center_x = x + square_size // 2
                        center_y = y + square_size // 2
                        cv2.circle(board_viz, (center_x, center_y), square_size // 3, piece_color, -1)
                        
                        # Add a highlight to make pieces more visible
                        cv2.circle(board_viz, (center_x, center_y), square_size // 3 - 5, 
                                  (piece_color[0] + 50, piece_color[1] + 50, piece_color[2] + 50), 3)
            
            # Add labels
            for i in range(8):
                # Column labels (0-7)
                cv2.putText(board_viz, str(i), (i * square_size + square_size // 2 - 10, 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Row labels (0-7)
                cv2.putText(board_viz, str(i), (10, i * square_size + square_size // 2 + 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Display both the original frame and the board visualization
            cv2.imshow("Camera View", frame)
            cv2.imshow("Board State", board_viz)
            cv2.waitKey(1)  # Short display time

# Test function for this module
def test_vision_system():
    """Test the vision system independently"""
    vision = VisionSystem()
    
    print("Initializing camera...")
    if not vision.init_camera():
        print("Failed to initialize camera. Exiting.")
        return
    
    try:
        while True:
            print("\nVision System Test Menu:")
            print("1. Capture and display frame")
            print("2. Detect board")
            print("3. Scan board for pieces")
            print("4. Exit")
            
            choice = input("Enter choice (1-4): ")
            
            if choice == "1":
                frame = vision.capture_frame()
                if frame is not None:
                    cv2.imshow("Camera Frame", frame)
                    cv2.waitKey(0)
                    cv2.destroyWindow("Camera Frame")
                
            elif choice == "2":
                frame = vision.capture_frame()
                if frame is not None:
                    corners = vision.detect_board(frame)
                    if corners is not None:
                        print("Board corners detected:")
                        for i, corner in enumerate(corners):
                            print(f"  Corner {i+1}: ({corner[0]:.1f}, {corner[1]:.1f})")
                        
                        # Draw corners on frame
                        for corner in corners:
                            cv2.circle(frame, (int(corner[0]), int(corner[1])), 5, (0, 255, 0), -1)
                        
                        cv2.imshow("Detected Board", frame)
                        cv2.waitKey(0)
                        cv2.destroyWindow("Detected Board")
                
            elif choice == "3":
                pieces = vision.scan_board()
                if pieces:
                    print(f"Detected {len(pieces)} pieces on the board")
                    vision.print_board_state(pieces)
                    input("Press Enter to continue...")
                    cv2.destroyAllWindows()
                
            elif choice == "4":
                print("Exiting test...")
                break
                
            else:
                print("Invalid choice. Please enter 1-4.")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        vision.release_camera()

if __name__ == "__main__":
    test_vision_system()