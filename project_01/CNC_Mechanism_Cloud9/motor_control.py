import Adafruit_BBIO.GPIO as GPIO
import time

# Define pins for all motors
X_STEP_PIN = "P2_2"
X_DIR_PIN = "P2_4"
Y1_STEP_PIN = "P2_6"
Y1_DIR_PIN = "P2_8"
Y2_STEP_PIN = "P2_22"
Y2_DIR_PIN = "P2_24"
Z_STEP_PIN = "P2_20"
Z_DIR_PIN = "P2_3"

# CNC Movement Configuration
STEPS_PER_MM_X = 80
STEPS_PER_MM_Y = 80
STEPS_PER_MM_Z = 400
STEP_DELAY = 0.0003
Z_STEP_DELAY = 0.0005

# Z-Axis Configuration
Z_MAX_HEIGHT = 100
Z_RELEASE_POSITION = 20
Z_TRAVEL_POSITION = 20

current_x = 0
current_y = 0
current_z = 0

check_limit_switch = None

# Store global XY limit positions
x_min_position = 0.0
x_max_position = 0.0
y_min_position = 0.0
y_max_position = 0.0

def init_motors():
    motor_pins = [X_STEP_PIN, X_DIR_PIN, Y1_STEP_PIN, Y1_DIR_PIN,
                  Y2_STEP_PIN, Y2_DIR_PIN, Z_STEP_PIN, Z_DIR_PIN]
    for pin in motor_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    print("Motors initialized")

def set_limit_check_function(check_function):
    global check_limit_switch
    check_limit_switch = check_function
    print("Limit switch checking enabled")

def set_limit_positions(x_min, x_max, y_min, y_max):
    global x_min_position, x_max_position, y_min_position, y_max_position
    x_min_position = x_min
    x_max_position = x_max
    y_min_position = y_min
    y_max_position = y_max

def get_limit_positions():
    return x_min_position, x_max_position, y_min_position, y_max_position

def move_x_axis(steps, direction, step_delay=STEP_DELAY):
    global current_x
    print(f"Moving X-axis {'forward' if direction else 'backward'} {steps} steps")
    GPIO.output(X_DIR_PIN, GPIO.HIGH if direction else GPIO.LOW)
    time.sleep(0.01)
    for i in range(steps):
        if check_limit_switch:
            if (direction and check_limit_switch('x_max')) or (not direction and check_limit_switch('x_min')):
                print(f"X-axis limit switch triggered at step {i}")
                break
        GPIO.output(X_STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(X_STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
        current_x += (1 / STEPS_PER_MM_X) if direction else -(1 / STEPS_PER_MM_X)

def move_y_axes(steps, direction, step_delay=STEP_DELAY):
    global current_y
    print(f"Moving Y-axes {'forward' if direction else 'backward'} {steps} steps")
    # FIXED DIRECTION INVERSION FOR Y
    GPIO.output(Y1_DIR_PIN, GPIO.LOW if direction else GPIO.HIGH)
    GPIO.output(Y2_DIR_PIN, GPIO.LOW if direction else GPIO.HIGH)
    time.sleep(0.01)
    for i in range(steps):
        if check_limit_switch:
            if (direction and check_limit_switch('y_max')) or (not direction and check_limit_switch('y_min')):
                print(f"Y-axis limit switch triggered at step {i}")
                break
        GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(Y1_STEP_PIN, GPIO.LOW)
        GPIO.output(Y2_STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
        current_y += (1 / STEPS_PER_MM_Y) if direction else -(1 / STEPS_PER_MM_Y)

def move_z_axis(steps, direction, step_delay=Z_STEP_DELAY):
    global current_z
    print(f"Moving Z-axis {'up' if direction else 'down'} {steps} steps")
    GPIO.output(Z_DIR_PIN, GPIO.LOW if direction else GPIO.HIGH)
    time.sleep(0.01)
    for i in range(steps):
        if check_limit_switch:
            if (direction and check_limit_switch('z_max')) or (not direction and check_limit_switch('z_min')):
                print(f"Z-axis limit switch triggered at step {i}")
                break
        GPIO.output(Z_STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(Z_STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
        current_z += (1 / STEPS_PER_MM_Z) if direction else -(1 / STEPS_PER_MM_Z)
    current_z = max(0, min(current_z, Z_MAX_HEIGHT))

def move_to_position(x_mm, y_mm, z_mm=None):
    global current_x, current_y, current_z

    # Limit enforcement
    if x_mm < x_min_position or x_mm > x_max_position:
        print(f"[Error] X target {x_mm:.2f}mm is outside [{x_min_position:.2f}, {x_max_position:.2f}] range!")
        return
    if y_mm < y_min_position or y_mm > y_max_position:
        print(f"[Error] Y target {y_mm:.2f}mm is outside [{y_min_position:.2f}, {y_max_position:.2f}] range!")
        return

    x_distance = x_mm - current_x
    x_steps = int(abs(x_distance) * STEPS_PER_MM_X)
    x_direction = x_distance > 0

    y_distance = y_mm - current_y
    y_steps = int(abs(y_distance) * STEPS_PER_MM_Y)
    y_direction = y_distance > 0

    z_is_low = (current_z <= Z_RELEASE_POSITION)
    lowering_z = (z_mm is not None and z_mm < current_z)

    if not z_is_low and lowering_z:
        move_z_axis(int(abs(current_z - z_mm) * STEPS_PER_MM_Z), False)

    if x_steps > 0:
        move_x_axis(x_steps, x_direction)
    if y_steps > 0:
        move_y_axes(y_steps, y_direction)

    if z_mm is not None:
        if z_mm > current_z:
            move_z_axis(int(abs(z_mm - current_z) * STEPS_PER_MM_Z), True)
        elif z_mm < current_z and z_is_low:
            move_z_axis(int(abs(current_z - z_mm) * STEPS_PER_MM_Z), False)

    print(f"[Beagle] move_to_position called with X={x_mm}, Y={y_mm}, Z={z_mm}")

def move_z(z_mm):
    global current_z
    z_distance = z_mm - current_z
    z_steps = int(abs(z_distance) * STEPS_PER_MM_Z)
    direction = z_distance > 0
    move_z_axis(z_steps, direction)

def get_current_position():
    return current_x, current_y, current_z

def set_current_position(x, y, z):
    global current_x, current_y, current_z
    current_x = x
    current_y = y
    current_z = z
    print(f"Position manually set to X:{x}mm Y:{y}mm Z:{z}mm")

def cleanup():
    GPIO.cleanup()
    print("GPIO pins cleaned up")

def test_motors():
    init_motors()
    try:
        move_to_position(100, 100, Z_RELEASE_POSITION)
        move_to_position(100, 100, Z_MAX_HEIGHT)
        time.sleep(1)
        move_to_position(100, 100, Z_RELEASE_POSITION)
        move_to_position(0, 0, Z_RELEASE_POSITION)
        print("Motor test complete")
    finally:
        cleanup()

if __name__ == "__main__":
    test_motors()
