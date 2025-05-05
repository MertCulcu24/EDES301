import cv2
import numpy as np
from typing import Tuple, Dict, Optional

class VisionSystem:
    def __init__(self):
        self.cap = None
        self.calibration_data = None
        self.board_corners = None
        self.squares = 8

    def init_camera(self) -> bool:
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            print("Camera initialized successfully on index 1")
            return True
        else:
            print("Error: Could not open camera at index 1")
            return False

    def release_camera(self) -> None:
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            print("Camera released")

    def capture_frame(self) -> Optional[np.ndarray]:
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        print("Error: Failed to capture frame")
        return None

    def detect_board(self, frame: np.ndarray) -> Optional[np.ndarray]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11, 2
        )

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("No contours found")
            return None

        h, w = frame.shape[:2]
        img_center = np.array([w / 2, h / 2])
        best = None
        best_score = float('inf')

        for cnt in contours:
            epsilon = 0.03 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) != 4:
                continue

            area = cv2.contourArea(approx)
            if area < 20000:
                continue

            x, y, width, height = cv2.boundingRect(approx)
            aspect_ratio = width / float(height)
            if aspect_ratio < 0.8 or aspect_ratio > 1.2:
                continue

            M = cv2.moments(approx)
            if M['m00'] == 0:
                continue

            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            center_dist = np.linalg.norm(np.array([cx, cy]) - img_center)

            if center_dist < best_score:
                best_score = center_dist
                best = approx

        if best is not None:
            corners = np.array([pt[0] for pt in best], dtype="float32")
            rect = self.order_points(corners)
            self.board_corners = rect
            return rect

        print("Error: Could not detect board corners")
        return None

    def order_points(self, pts: np.ndarray) -> np.ndarray:
        s = pts.sum(axis=1)
        rect = np.zeros((4, 2), dtype="float32")
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def detect_pieces(self, frame: np.ndarray) -> Dict[Tuple[int, int], str]:
        if self.board_corners is None:
            self.detect_board(frame)
            if self.board_corners is None:
                return {}

        width, height = 800, 800
        dst = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")
        M = cv2.getPerspectiveTransform(self.board_corners, dst)
        warped = cv2.warpPerspective(frame, M, (width, height))

        pieces = {}
        square_size = width // self.squares

        for row in range(self.squares):
            for col in range(self.squares):
                print(f"Analyzing square at (col={col}, row={row})")
                x = col * square_size
                y = row * square_size
                square = warped[y:y+square_size, x:x+square_size]
                piece_type = self.identify_piece(square)
                if piece_type:
                    pieces[(col, row)] = piece_type
                    cv2.rectangle(warped, (x, y), (x+square_size, y+square_size), (0, 255, 0), 2)
                    cv2.putText(warped, piece_type, (x+5, y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Detected Pieces", warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return pieces

    def identify_piece(self, square: np.ndarray) -> Optional[str]:
        if square.size == 0:
            return None

        hsv = cv2.cvtColor(square, cv2.COLOR_BGR2HSV)
        center = square.shape[0] // 4
        center_region = square[center:center*3, center:center*3]
        avg_hsv = np.mean(center_region, axis=(0, 1))
        std_scalar = np.mean(np.std(center_region, axis=(0, 1)))

        h, s, v = avg_hsv
        print(f"→ H: {h:.1f}, S: {s:.1f}, V: {v:.1f}, Std: {std_scalar:.1f}")

        if v < 220 and s < 180 and std_scalar > 12:
            return 'B'

        return None

    def scan_board(self) -> Dict[Tuple[int, int], str]:
        frame = self.capture_frame()
        if frame is None:
            return {}

        if self.board_corners is None:
            self.detect_board(frame)
            if self.board_corners is None:
                return {}

        pieces = self.detect_pieces(frame)
        self.display_board_state(pieces, frame)
        return pieces

    def print_board_state(self, pieces: Dict[Tuple[int, int], str]) -> None:
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
        if frame is None:
            frame = self.capture_frame()
            if frame is None:
                return

        if self.board_corners is not None:
            for i, corner in enumerate(self.board_corners):
                cv2.circle(frame, (int(corner[0]), int(corner[1])), 5, (0, 255, 0), -1)
                cv2.putText(frame, str(i), (int(corner[0]), int(corner[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Camera View", frame)
        cv2.waitKey(1)
