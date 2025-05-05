# cnc_checkers.py — Main VS Code Controller
import time
from vision_system import VisionSystem
from board_system import BoardSystem
from calibration_system import CalibrationSystem
import remote_motor_control as rmc

class CNCCheckers:
    def __init__(self):
        self.board = BoardSystem()
        self.vision = VisionSystem()
        self.calibration = CalibrationSystem(self.vision, self.board)

        print("[System] Initializing...")
        self.vision.init_camera()
        self.calibration.load()
        print("[System] Ready.")

    def move_piece(self, start, end):
        x1, y1 = start
        x2, y2 = end

        if not all(0 <= v < 8 for v in [x1, y1, x2, y2]):
            print("[Move] Invalid square")
            return

        start_x, start_y = self.board.board_to_cnc(x1, y1)
        end_x, end_y = self.board.board_to_cnc(x2, y2)

        Z_ATTACH = 10.0
        Z_PLACE  = 2.0
        Z_LOW    = 0.0

        rmc.jog_to(start_x, start_y, Z_LOW)
        rmc.jog_to(start_x, start_y, Z_ATTACH)
        time.sleep(0.2)

        rmc.jog_to(end_x, end_y, Z_ATTACH)
        rmc.jog_to(end_x, end_y, Z_PLACE)
        time.sleep(0.2)

        rmc.jog_to(end_x, end_y, Z_LOW)
        print("[Move] Piece moved.")

    def menu(self):
        while True:
            print("\n=== CNC Checkers ===")
            print("1. Calibrate board")
            print("2. Move piece")
            print("3. Show camera")
            print("4. Exit")

            choice = input("Select: ")
            if choice == "1":
                self.calibration.run()
            elif choice == "2":
                try:
                    x1 = int(input("Start X: "))
                    y1 = int(input("Start Y: "))
                    x2 = int(input("End X: "))
                    y2 = int(input("End Y: "))
                    self.move_piece((x1, y1), (x2, y2))
                except ValueError:
                    print("[Input] Invalid coordinates")
            elif choice == "3":
                frame = self.vision.capture_frame()
                if frame is not None:
                    self.vision.detect_board(frame)
                    pieces = self.vision.detect_pieces(frame)
                    self.vision.display_board_state(pieces, frame)
            elif choice == "4":
                print("Exiting...")
                self.vision.release_camera()
                break
            else:
                print("Invalid option")

if __name__ == "__main__":
    CNCCheckers().menu()