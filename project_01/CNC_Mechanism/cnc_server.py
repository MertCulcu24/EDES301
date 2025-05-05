# cnc_server.py — Fresh TCP Server with XY limit reporting

import socket
import motor_control as mc
import home_cnc as hc

HOST = '0.0.0.0'
PORT = 9999

def handle_command(command):
    parts = command.strip().split()
    if not parts:
        return "EMPTY\n"

    if parts[0] == "JOG_TO" and len(parts) == 4:
        try:
            x, y, z = map(float, parts[1:])
            mc.move_to_position(x, y, z)
            return "OK\n"
        except ValueError:
            return "BAD JOG FORMAT\n"

    elif parts[0] == "MOVE" and len(parts) == 5:
        try:
            x1, y1, x2, y2 = map(int, parts[1:])
            return f"Move logic for board squares {x1},{y1} → {x2},{y2} not yet implemented\n"
        except ValueError:
            return "BAD MOVE FORMAT\n"

    elif parts[0] == "GET_POSITION":
        x, y, z = mc.get_current_position()
        return f"POS {x:.2f} {y:.2f} {z:.2f}\n"

    elif parts[0] == "GET_XY_LIMITS":
        x_min, x_max, y_min, y_max = mc.get_limit_positions()
        return f"{x_min:.2f},{x_max:.2f},{y_min:.2f},{y_max:.2f}\n"

    return "UNKNOWN CMD\n"

def main():
    print("[Beagle] Initializing system...")
    mc.init_motors()
    hc.init_limit_switches()
    hc.home_cnc(mc)

    print(f"[Beagle] Listening on {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        while True:
            conn, addr = server.accept()
            with conn:
                print(f"[Beagle] Connection from {addr}")
                data = conn.recv(1024).decode().strip()
                if data:
                    print(f"[Beagle] Received: {data}")
                    response = handle_command(data)
                    conn.sendall(response.encode())

if __name__ == "__main__":
    main()
