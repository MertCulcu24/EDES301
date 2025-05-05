from typing import Tuple

class BoardSystem:
    """
    System for handling board coordinates and conversion to CNC coordinates
    """

    def __init__(self, board_size_mm: float = 200.0, squares: int = 8):
        """
        Initialize the board system with board dimensions
        """
        self.board_size_mm = board_size_mm
        self.squares = squares
        self.square_size_mm = board_size_mm / squares
        self.board_offset_x = 0.0
        self.board_offset_y = 0.0

    def is_valid_square(self, x: int, y: int) -> bool:
        """
        Check if the given board coordinates are valid (within the 8x8 board)
        """
        return 0 <= x < self.squares and 0 <= y < self.squares

    def board_to_cnc(self, board_x: float, board_y: float) -> Tuple[float, float]:
        """
        Convert board coordinates (0–7) to CNC coordinates in mm.
        The CNC target is the *center* of the square.
        """
        if isinstance(board_x, int):
            board_x += 0.5
        if isinstance(board_y, int):
            board_y += 0.5

        cnc_x = self.board_offset_x + board_x * self.square_size_mm
        cnc_y = self.board_offset_y + board_y * self.square_size_mm
        return cnc_x, cnc_y

    def cnc_to_board(self, cnc_x: float, cnc_y: float) -> Tuple[int, int]:
        """
        Convert CNC coordinates (in mm) back to board squares (0–7)
        """
        x_relative = cnc_x - self.board_offset_x
        y_relative = cnc_y - self.board_offset_y

        board_x = int(x_relative / self.square_size_mm)
        board_y = int(y_relative / self.square_size_mm)

        return board_x, board_y

    def set_board_offset(self, offset_x: float, offset_y: float) -> None:
        """
        Set the offset from the CNC origin to the bottom-left of the board
        """
        self.board_offset_x = offset_x
        self.board_offset_y = offset_y
        print(f"Board offset set to ({offset_x:.2f}, {offset_y:.2f}) mm")

    def set_square_size(self, size_mm: float) -> None:
        """
        Set square size and adjust the board size accordingly
        """
        self.square_size_mm = size_mm
        self.board_size_mm = size_mm * self.squares
        print(f"Square size set to {size_mm:.2f} mm — board size is now {self.board_size_mm:.2f} mm")
