# board_system.py — Auto-calibrated from CNC-reported axis limits
class BoardSystem:
    def __init__(self):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.board_size_mm = 300.0
        self.square_size_x = 37.5
        self.square_size_y = 37.5
        self.x_min = 0.0
        self.y_min = 0.0

    def set_offset(self, x: float, y: float):
        self.offset_x = x
        self.offset_y = y

    def set_board_size(self, size: float):
        self.board_size_mm = size
        self.square_size_x = size / 8
        self.square_size_y = size / 8

    def set_axis_limits(self, x_min, x_max, y_min, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.square_size_x = (x_max - x_min) / 8
        self.square_size_y = (y_max - y_min) / 8 

    def board_to_cnc(self, col: int, row: int) -> tuple[float, float]:
        x = self.x_min + (col + 1) * self.square_size_x
        y = self.y_min + (row + 1) * self.square_size_y
        return x, y