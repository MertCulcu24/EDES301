# calibration_system.py — Uses actual CNC homed position for vision calibration
import numpy as np
from vision_system import VisionSystem
from board_system import BoardSystem
import remote_motor_control as rmc
import cv2
import msvcrt

class CalibrationSystem:
    def __init__(self, vision: VisionSystem, board: BoardSystem):
        self.vision = vision
        self.board = board
        self.calibration_data = None

    def run(self) -> bool:
        print("Select calibration mode:")
        print("1. Use physical board size (e.g. 300mm)")
        print("2. Manually jog to each CNC board corner")
        print("3. Auto from CNC XY limits")
        mode = input("Select mode (1, 2, or 3): ").strip()

        if mode == "1":
            return self._run_fixed_size_mode()
        elif mode == "2":
            return self._run_manual_jog_mode()
        elif mode == "3":
            return self._run_limit_based_mode()
        else:
            print("Invalid selection")
            return False

    def _run_fixed_size_mode(self) -> bool:
        print("[Calib] Capturing board corners using camera...")
        frame = self.vision.capture_frame()
        if frame is None:
            print("[Calib] Failed to capture image")
            return False

        corners = self.vision.detect_board(frame)
        if corners is None:
            print("[Calib] Board corners not detected")
            return False

        for i, corner in enumerate(corners):
            x, y = int(corner[0]), int(corner[1])
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(frame, str(i), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Calibration Preview", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        confirm = input("Use these corners? (y/n): ").strip().lower()
        if confirm != 'y':
            print("[Calib] Calibration cancelled by user")
            return False

        print("[Calib] Corners confirmed.")

        try:
            board_size = float(input("Enter physical board size in mm (e.g. 300): "))
        except ValueError:
            print("[Calib] Invalid input")
            return False

        home_x, home_y, _ = rmc.get_position()
        print(f"[Calib] CNC homed position: X={home_x:.2f} mm, Y={home_y:.2f} mm")

        offset_x = home_x - board_size / 2
        offset_y = home_y - board_size / 2

        self.board.set_offset(offset_x, offset_y)
        self.board.set_board_size(board_size)
        self.vision.board_corners = corners

        self.calibration_data = {
            "offset_x": offset_x,
            "offset_y": offset_y,
            "board_size": board_size,
            "image_corners": corners.tolist()
        }

        np.savez("calibration_data.npz", **self.calibration_data)
        print("[Calib] Calibration saved to calibration_data.npz")
        return True

    def _run_manual_jog_mode(self) -> bool:
        print("[Manual] Jog CNC to each board corner using keyboard. Press Enter to record each corner.")

        print("→ Bottom-left (square 0,0):")
        self._keyboard_jog_loop("bottom-left")
        bl_x, bl_y, _ = rmc.get_position()

        print("→ Bottom-right (square 7,0):")
        self._keyboard_jog_loop("bottom-right")
        br_x, br_y, _ = rmc.get_position()

        print("→ Top-right (square 7,7):")
        self._keyboard_jog_loop("top-right")
        tr_x, tr_y, _ = rmc.get_position()

        print("→ Top-left (square 0,7):")
        self._keyboard_jog_loop("top-left")
        tl_x, tl_y, _ = rmc.get_position()

        width = br_x - bl_x
        height = tl_y - bl_y

        offset_x = bl_x
        offset_y = bl_y

        board_size = (width + height) / 2

        self.board.set_offset(offset_x, offset_y)
        self.board.set_board_size(board_size)

        self.calibration_data = {
            "offset_x": offset_x,
            "offset_y": offset_y,
            "board_size": board_size,
            "corners_manual": [(bl_x, bl_y), (br_x, br_y), (tr_x, tr_y), (tl_x, tl_y)]
        }

        np.savez("calibration_data.npz", **self.calibration_data)
        print("[Calib] Jog-based calibration complete and saved.")
        return True

    def _run_limit_based_mode(self) -> bool:
        print("[Calib] Requesting CNC axis limits...")
        limits = rmc.get_xy_limits()
        if limits is None:
            print("[Calib] Failed to get XY limits from Beagle")
            return False

        x_min, x_max, y_min, y_max = limits
        self.board.set_axis_limits(x_min, x_max, y_min, y_max)
        print(f"[Calib] Limits received: X=({x_min:.2f}, {x_max:.2f}), Y=({y_min:.2f}, {y_max:.2f})")
        print("[Calib] Board system now uses square size based on CNC travel range")

        self.calibration_data = {
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
            "square_size_x": (x_max - x_min) / 8,
            "square_size_y": (y_max - y_min) / 8
        }

        np.savez("calibration_data.npz", **self.calibration_data)
        print("[Calib] Limit-based calibration saved to calibration_data.npz")
        return True

    def _keyboard_jog_loop(self, label: str):
        print(f"\n[Jog] Use w/a/s/d to move XY, q/e for Z. Press Enter when at {label} corner.")
        jog_step = 1.0  # mm
        x, y, z = rmc.get_position()

        while True:
            print(f"  Current position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}   (Press Enter to confirm)")
            key = msvcrt.getch()
            try:
                key = key.decode('utf-8').lower()
            except UnicodeDecodeError:
                print("[Jog] Non-standard key pressed — ignored")
                continue

            if key == '\r':  # Enter key
                break
            elif key == 'w': y += jog_step
            elif key == 's': y -= jog_step
            elif key == 'a': x -= jog_step
            elif key == 'd': x += jog_step
            elif key == 'q': z += jog_step
            elif key == 'e': z -= jog_step

            rmc.jog_to(x, y, z)

    def load(self):
        try:
            data = np.load("calibration_data.npz")
            self.board.set_offset(float(data.get('offset_x', 0)), float(data.get('offset_y', 0)))
            self.board.set_board_size(float(data.get('board_size', 300.0)))
            if "image_corners" in data:
                self.vision.board_corners = np.array(data['image_corners'])
            if "x_min" in data:
                self.board.set_axis_limits(
                    float(data["x_min"]), float(data["x_max"]),
                    float(data["y_min"]), float(data["y_max"])
                )
            print("[Calib] Calibration loaded from file")
            return True
        except Exception as e:
            print(f"[Calib] Failed to load: {e}")
            return False
