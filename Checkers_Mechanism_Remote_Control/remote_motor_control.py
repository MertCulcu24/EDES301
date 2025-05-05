# remote_motor_control.py — Client for Windows Side

import socket

POCKETBEAGLE_IP = '192.168.7.2'
PORT = 9999

def send_command(cmd: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((POCKETBEAGLE_IP, PORT))
        s.sendall((cmd + "\n").encode())
        return s.recv(1024).decode().strip()

def jog_to(x: float, y: float, z: float):
    print(f"[Remote] Jog to X={x:.2f} Y={y:.2f} Z={z:.2f}")
    return send_command(f"JOG_TO {x:.2f} {y:.2f} {z:.2f}")

def get_position():
    response = send_command("GET_POSITION")
    if response.startswith("POS"):
        _, x, y, z = response.split()
        return float(x), float(y), float(z)
    else:
        print("[Remote] Failed to get position")
        return None

def get_xy_limits():
    response = send_command("GET_XY_LIMITS")
    try:
        x_min, x_max, y_min, y_max = map(float, response.split(","))
        return x_min, x_max, y_min, y_max
    except ValueError:
        print("[Remote] Failed to parse XY limits:", response)
        return None

if __name__ == "__main__":
    print("Jogging test:")
    jog_to(10, 10, 2)
    print("Position:", get_position())
    print("XY Limits:", get_xy_limits())
