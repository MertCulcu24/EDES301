import Adafruit_BBIO.GPIO as GPIO
import time

# Define pins for all motors
X_STEP_PIN = "P2_2"
X_DIR_PIN = "P2_4"

# Y motors (both will be controlled together)
Y1_STEP_PIN = "P2_6"  # First Y motor
Y1_DIR_PIN = "P2_8"
Y2_STEP_PIN = "P2_22"  # Second Y motor
Y2_DIR_PIN = "P2_24"

# Z motor
Z_STEP_PIN = "P2_20"
Z_DIR_PIN = "P2_18"

# Setup all GPIO pins
pins = [X_STEP_PIN, X_DIR_PIN, Y1_STEP_PIN, Y1_DIR_PIN, 
        Y2_STEP_PIN, Y2_DIR_PIN, Z_STEP_PIN, Z_DIR_PIN]

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def move_x_axis(steps, direction, step_delay=0.001):
    """Move X axis motor"""
    print(f"Moving X-axis {'forward' if direction else 'backward'}")
    GPIO.output(X_DIR_PIN, GPIO.HIGH if direction else GPIO.LOW)
    time.sleep(0.01)  # Direction signal settle time
    
    for i in range(steps):
        GPIO.output(X_STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(X_STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
        
        if i % 100 == 0:
            print(f"X Step {i}/{steps}")

def move_y_axes(steps, direction, step_delay=0.001):
    """Move both Y axis motors simultaneously"""
    print(f"Moving Y-axes {'forward' if direction else 'backward'}")
    GPIO.output(Y1_DIR_PIN, GPIO.HIGH if direction else GPIO.LOW)
    GPIO.output(Y2_DIR_PIN, GPIO.HIGH if direction else GPIO.LOW)
    time.sleep(0.01)  # Direction signal settle time
    
    for i in range(steps):
        # Pulse both Y motors at the same time
        GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(Y1_STEP_PIN, GPIO.LOW)
        
        GPIO.output(Y2_STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
        
        if i % 100 == 0:
            print(f"Y Step {i}/{steps}")

def move_z_axis(steps, direction, step_delay=0.001):
    """Move Z axis motor"""
    print(f"Moving Z-axis {'up' if direction else 'down'}")
    GPIO.output(Z_DIR_PIN, GPIO.HIGH if direction else GPIO.LOW)
    time.sleep(0.01)  # Direction signal settle time
    
    for i in range(steps):
        GPIO.output(Z_STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(Z_STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)
        
        if i % 100 == 0:
            print(f"Z Step {i}/{steps}")

# New function for 10-second Y-axis rotation
def run_y_motors_for_duration(direction, duration_seconds, step_delay=0.0002):
    """Run Y motors for a specific duration in one direction"""
    print(f"Running Y motors {'forward' if direction else 'backward'} for {duration_seconds} seconds")
    
    # Calculate number of steps based on duration and step delay
    # Each step cycle takes 2 * step_delay time
    steps_per_second = int(1.0 / (2 * step_delay))
    total_steps = steps_per_second * duration_seconds
    
    move_y_axes(total_steps, direction, step_delay)

def test_motor(motor_name):
    """Test a specific motor or motor group"""
    steps = 600  # Adjust as needed
    
    if motor_name == "x":
        move_x_axis(steps, True)
        time.sleep(0.5)
        move_x_axis(steps, False)
    elif motor_name == "y":
        move_y_axes(steps, True)
        time.sleep(0.5)
        move_y_axes(steps, False)
    elif motor_name == "z":
        move_z_axis(steps, True)
        time.sleep(0.5)
        move_z_axis(steps, False)
    elif motor_name == "all":
        # Test all motors in sequence
        move_x_axis(steps, True)
        time.sleep(0.5)
        move_x_axis(steps, False)
        time.sleep(1)
        
        move_y_axes(steps, True)
        time.sleep(0.5)
        move_y_axes(steps, False)
        time.sleep(1)
        
        move_z_axis(steps, True)
        time.sleep(0.5)
        move_z_axis(steps, False)

# New function for 10 seconds each direction Y-axis test
def test_y_motors_timed():
    """Run Y motors for 10 seconds in one direction, then 10 seconds in the other"""
    print("Running Y motors for 10 seconds in each direction")
    
    # First direction (forward)
    run_y_motors_for_duration(True, 10)
    time.sleep(1)  # Pause between directions
    
    # Second direction (backward)
    run_y_motors_for_duration(False, 10)
    
    print("Timed Y motor test complete")

try:
    print("CNC Motor Test Program")
    print("---------------------")
    
    while True:
        print("\nSelect test to run:")
        print("1. Test X motor")
        print("2. Test Y motors (both Y1 and Y2 together)")
        print("3. Test Z motor")
        print("4. Test all motors in sequence")
        print("5. Run Y motors 10 seconds each direction")
        print("6. Exit")
        
        choice = input("Enter choice (1-6): ")
        
        if choice == "1":
            test_motor("x")
        elif choice == "2":
            test_motor("y")
        elif choice == "3":
            test_motor("z")
        elif choice == "4":
            test_motor("all")
        elif choice == "5":
            test_y_motors_timed()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-6.")
            
except KeyboardInterrupt:
    print("\nTest interrupted by user")
finally:
    # Clean up GPIO
    GPIO.cleanup()
    print("GPIO cleaned up")