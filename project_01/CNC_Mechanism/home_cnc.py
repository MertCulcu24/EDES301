import Adafruit_BBIO.GPIO as GPIO
import time


# Import pins and configuration constants from motor_control
# In a real implementation, you might want to put these in a shared config file
from motor_control import (
    X_STEP_PIN, X_DIR_PIN,
    Y1_STEP_PIN, Y1_DIR_PIN,
    Y2_STEP_PIN, Y2_DIR_PIN,
    Z_STEP_PIN, Z_DIR_PIN,
    STEPS_PER_MM_X, STEPS_PER_MM_Y, STEPS_PER_MM_Z
)

# Define pins for limit switches - using 6 total switches
X_MIN_LIMIT_PIN = "P1_2"    # X-axis minimum (home) position limit switch
X_MAX_LIMIT_PIN = "P1_4"    # X-axis maximum position limit switch
Y_MIN_LIMIT_PIN = "P1_34"   # Y-axis minimum (home) position limit switch
Y_MAX_LIMIT_PIN = "P1_20"   # Y-axis maximum position limit switch
Z_MIN_LIMIT_PIN = "P2_19"   # Z-axis minimum (home) position limit switch
Z_MAX_LIMIT_PIN = "P2_33"   # Z-axis maximum position limit switch

# Homing configuration
HOMING_SPEED_FAST = 0.0002  # Faster approach speed (was 0.0005)
HOMING_SPEED_SLOW = 0.0005  # Faster final approach speed (was 0.002)
HOMING_BACKOFF = 10         # mm to back off after hitting limit switch (increased from 5 to 10)
MAX_HOMING_DISTANCE = 2000  # Maximum travel distance when seeking home (safety limit)

# Safety margins for Z-axis
Z_MAX_SAFETY_MARGIN = 1    # mm to stay away from absolute maximum
Z_MIN_SAFETY_MARGIN = 5    # mm to stay away from absolute minimum
z_max_travel = 0           # Will be set during homing

def init_limit_switches():
    """Initialize all limit switch pins with pull-up resistors"""
    # Setup limit switch pins with pull-up resistors
    limit_pins = [
        X_MIN_LIMIT_PIN, X_MAX_LIMIT_PIN, 
        Y_MIN_LIMIT_PIN, Y_MAX_LIMIT_PIN,
        Z_MIN_LIMIT_PIN, Z_MAX_LIMIT_PIN
    ]
    
    for pin in limit_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    print("Limit switches initialized")

def check_limit_switch(limit_pin):
    """Check if a limit switch is triggered (returns True if triggered)"""
    # With pull-up resistors, switch is triggered when input reads LOW
    return GPIO.input(limit_pin) == GPIO.LOW

def check_axis_limits():
    """
    Check all limit switches and return a dictionary of their states
    True means the switch is triggered (axis at limit)
    """
    return {
        'x_min': check_limit_switch(X_MIN_LIMIT_PIN),
        'x_max': check_limit_switch(X_MAX_LIMIT_PIN),
        'y_min': check_limit_switch(Y_MIN_LIMIT_PIN),
        'y_max': check_limit_switch(Y_MAX_LIMIT_PIN),
        'z_min': check_limit_switch(Z_MIN_LIMIT_PIN),
        'z_max': check_limit_switch(Z_MAX_LIMIT_PIN)
    }

def home_cnc(motor_control):
    """
    Home all axes to their zero positions using limit switches
    
    Args:
        motor_control: Reference to the motor_control module to update positions
    """
    print("Homing all axes...")
    
    # First home Z axis for safety (move away from board)
    home_z_axis(motor_control)
    
    # Then home X and Y axes
    home_x_axis(motor_control)
    home_y_axes(motor_control)
    #motor_control.set_current_position(0.0, 0.0, 0.0)
    #print("[Home] Homed position set as origin: (0, 0, 0)")
    print("Homing complete")
 

def home_z_axis(motor_control):
    """
    Home the Z axis with direct limit switch checking and corrected direction logic
    
    Args:
        motor_control: Reference to the motor_control module to update position
    """
    global z_max_travel
    
    print("Homing Z axis with corrected direction logic...")
    
    # Step 1: First go to Z-MIN (lower limit) to establish the minimum boundary
    print("Step 1: Moving to Z-MIN position...")
    
    # Check if already at Z-MIN limit switch
    current_z_min_status = GPIO.input(Z_MIN_LIMIT_PIN) == GPIO.LOW
    print(f"Z-MIN limit switch initial status: {'TRIGGERED' if current_z_min_status else 'not triggered'}")
    
    if current_z_min_status:
        print("Z axis already at MIN limit position")
        # Back off slightly
        print("Backing off from Z-MIN (moving UP)...")
        
        # LOW = UP (away from MIN) based on your test
        GPIO.output(Z_DIR_PIN, GPIO.LOW)
        time.sleep(0.1)  # Direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_Z)):
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            motor_control.current_z += 1 / STEPS_PER_MM_Z
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off: {i} steps, position: {motor_control.current_z:.2f}mm")
    else:
        # Move Z down until MIN limit switch is triggered or safety limit reached
        print("Moving DOWN toward Z-MIN...")
        
        # HIGH = DOWN (toward MIN) based on your test
        GPIO.output(Z_DIR_PIN, GPIO.HIGH)
        time.sleep(0.1)  # Direction signal settle time
        
        steps_taken = 0
        max_steps = int(MAX_HOMING_DISTANCE * STEPS_PER_MM_Z)
        
        # Fast approach to Z-MIN
        while steps_taken < max_steps:
            # First check limit switch - Check at beginning of each loop
            if GPIO.input(Z_MIN_LIMIT_PIN) == GPIO.LOW:
                print(f"Z-MIN limit switch triggered after {steps_taken} steps")
                time.sleep(0.01)  # Small delay to ensure the signal is stable
                # Check again to confirm it wasn't a false trigger
                if GPIO.input(Z_MIN_LIMIT_PIN) == GPIO.LOW:
                    break
                
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            steps_taken += 1
            
            # Update position tracking
            motor_control.current_z -= 1 / STEPS_PER_MM_Z
            
            if steps_taken % 100 == 0:
                print(f"Moving to Z-MIN: {steps_taken} steps, position: {motor_control.current_z:.2f}mm")
        
        # If we hit the safety limit without finding MIN, report error
        if steps_taken >= max_steps:
            print("ERROR: Z-axis failed to find minimum limit within safety limit")
            return False
        
        print(f"Z axis reached MIN position at {motor_control.current_z:.2f}mm")
        
        # Back off from Z-MIN
        print("Backing off from Z-MIN (moving UP)...")
        
        # LOW = UP (away from MIN) based on your test
        GPIO.output(Z_DIR_PIN, GPIO.LOW)
        time.sleep(0.1)  # Direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_Z)):
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            motor_control.current_z += 1 / STEPS_PER_MM_Z
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off: {i} steps, position: {motor_control.current_z:.2f}mm")
    
    # Store the Z-MIN position (with backoff already applied)
    z_min_position = motor_control.current_z
    print(f"Z-MIN position (with backoff): {z_min_position:.2f}mm")
    
    # Add a pause before changing direction
    print("Pausing before moving to Z-MAX...")
    time.sleep(0.5)  # 500ms pause
    
    # Step 2: Now go to Z-MAX to determine the maximum travel range
    print("\nStep 2: Moving to Z-MAX position...")
    
    # Check Z-MAX limit switch status
    current_z_max_status = GPIO.input(Z_MAX_LIMIT_PIN) == GPIO.LOW
    print(f"Z-MAX limit switch initial status: {'TRIGGERED' if current_z_max_status else 'not triggered'}")
    
    # First check if already at the MAX limit switch
    if current_z_max_status:
        print("Z axis already at MAX limit position")
        # Back off slightly
        print("Backing off from Z-MAX (moving DOWN)...")
        
        # HIGH = DOWN (away from MAX) based on your test
        GPIO.output(Z_DIR_PIN, GPIO.HIGH)
        time.sleep(0.1)  # Direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_Z)):
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            motor_control.current_z -= 1 / STEPS_PER_MM_Z
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off: {i} steps, position: {motor_control.current_z:.2f}mm")
    else:
        # Move Z toward MAX until limit switch is triggered or safety limit reached
        print("Moving UP toward Z-MAX...")
        
        # LOW = UP (toward MAX) based on your test
        GPIO.output(Z_DIR_PIN, GPIO.LOW)
        time.sleep(0.1)  # Direction signal settle time
        
        steps_taken = 0
        max_steps = int(MAX_HOMING_DISTANCE * STEPS_PER_MM_Z)
        
        # Fast approach to Z-MAX
        while steps_taken < max_steps:
            # First check limit switch at the beginning of each loop
            if GPIO.input(Z_MAX_LIMIT_PIN) == GPIO.LOW:
                print(f"Z-MAX limit switch triggered after {steps_taken} steps")
                time.sleep(0.01)  # Small delay to ensure the signal is stable
                # Check again to confirm it wasn't a false trigger
                if GPIO.input(Z_MAX_LIMIT_PIN) == GPIO.LOW:
                    break
                
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            
            steps_taken += 1
            
            # Update position tracking
            motor_control.current_z += 1 / STEPS_PER_MM_Z
            
            if steps_taken % 100 == 0:
                print(f"Moving to Z-MAX: {steps_taken} steps, position: {motor_control.current_z:.2f}mm")
        
        # If we hit the safety limit without finding MAX, report error
        if steps_taken >= max_steps:
            print("ERROR: Z-axis failed to find maximum limit within safety limit")
            # Set a default value
            z_max_travel = 100
            return False
        
        print(f"Z axis reached MAX position at {motor_control.current_z:.2f}mm")
        
        # Back off from Z-MAX
        print("Backing off from Z-MAX (moving DOWN)...")
        
        # HIGH = DOWN (away from MAX) based on your test
        GPIO.output(Z_DIR_PIN, GPIO.HIGH)
        time.sleep(0.1)  # Direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_Z)):
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            motor_control.current_z -= 1 / STEPS_PER_MM_Z
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off: {i} steps, position: {motor_control.current_z:.2f}mm")
    
    # Store the Z-MAX position (with backoff already applied)
    z_max_position = motor_control.current_z
    print(f"Z-MAX position (with backoff): {z_max_position:.2f}mm")
    
    # Calculate total Z travel range
    z_travel_range = abs(z_max_position - z_min_position)
    print(f"Total Z travel range: {z_travel_range:.2f}mm")
    
    # Store the computed travel range
    z_max_travel = z_travel_range
    
    # Calculate operational Z positions
    motor_control.Z_MAX_HEIGHT = z_max_position - Z_MAX_SAFETY_MARGIN
    motor_control.Z_RELEASE_POSITION = z_min_position + Z_MIN_SAFETY_MARGIN
    motor_control.Z_TRAVEL_POSITION = z_min_position + Z_MIN_SAFETY_MARGIN
    
    print(f"Z max height set to: {motor_control.Z_MAX_HEIGHT:.2f}mm")
    print(f"Z release position set to: {motor_control.Z_RELEASE_POSITION:.2f}mm")
    
    # Step 3: Move to a safe release position
    print(f"Moving Z to release position ({motor_control.Z_RELEASE_POSITION:.2f}mm)...")
    
    # Calculate steps to move to release position
    current_z = motor_control.current_z
    
    if current_z > motor_control.Z_RELEASE_POSITION:
        # Need to move DOWN
        steps_to_move = int((current_z - motor_control.Z_RELEASE_POSITION) * STEPS_PER_MM_Z)
        print(f"Moving DOWN {steps_to_move} steps to reach release position...")
        
        # HIGH = DOWN based on your test
        GPIO.output(Z_DIR_PIN, GPIO.HIGH)
        time.sleep(0.1)  # Direction signal settle time
        
        for i in range(steps_to_move):
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            motor_control.current_z -= 1 / STEPS_PER_MM_Z
            
            if i % 100 == 0 and i > 0:
                print(f"Moving to release position: {i} steps, position: {motor_control.current_z:.2f}mm")
    else:
        # Need to move UP
        steps_to_move = int((motor_control.Z_RELEASE_POSITION - current_z) * STEPS_PER_MM_Z)
        print(f"Moving UP {steps_to_move} steps to reach release position...")
        
        # LOW = UP based on your test
        GPIO.output(Z_DIR_PIN, GPIO.LOW)
        time.sleep(0.1)  # Direction signal settle time
        
        for i in range(steps_to_move):
            GPIO.output(Z_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Z_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            motor_control.current_z += 1 / STEPS_PER_MM_Z
            
            if i % 100 == 0 and i > 0:
                print(f"Moving to release position: {i} steps, position: {motor_control.current_z:.2f}mm")
    
    # Set current position to release position
    motor_control.current_z = motor_control.Z_RELEASE_POSITION
    print(f"Z axis at release position ({motor_control.Z_RELEASE_POSITION:.2f}mm)")
    print("Z axis homed successfully")
    
    return True
    
def home_x_axis(motor_control):
    """
    Home the X axis first to MIN then to MAX with robust limit switch detection
    
    Args:
        motor_control: Reference to the motor_control module to update position
    """
    print("Homing X axis with fixed direction logic...")
    
    # STEP 1: Home to X-MIN first
    print("\nSTEP 1: Moving to X-MIN position...")
    
    # Check if already at X-MIN limit switch
    if check_limit_switch(X_MIN_LIMIT_PIN):
        print("X axis already at MIN limit position")
        # Back off slightly
        print("Backing off from X-MIN...")
        
        # Direction: away from MIN (HIGH)
        GPIO.output(X_DIR_PIN, GPIO.HIGH)
        time.sleep(0.2)  # Longer direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_X)):
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_x += 1 / STEPS_PER_MM_X
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off from MIN: {i} steps, position: {motor_control.current_x:.2f}mm")
    else:
        # Move X toward MIN until limit switch is triggered or safety limit reached
        print("Moving toward X-MIN...")
        
        # Direction: toward MIN (LOW)
        GPIO.output(X_DIR_PIN, GPIO.LOW)
        time.sleep(0.2)  # Longer direction signal settle time
        
        steps_taken = 0
        max_steps = int(MAX_HOMING_DISTANCE * STEPS_PER_MM_X)
        
        # Fast approach to X-MIN
        while steps_taken < max_steps:
            # Check limit switch at beginning of each loop iteration
            if check_limit_switch(X_MIN_LIMIT_PIN):
                print(f"X-MIN limit switch triggered after {steps_taken} steps")
                time.sleep(0.05)  # Longer delay to ensure signal is stable
                # Double-check to avoid false triggers
                if check_limit_switch(X_MIN_LIMIT_PIN):
                    break
                
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            steps_taken += 1
            
            # Update position tracking
            motor_control.current_x -= 1 / STEPS_PER_MM_X
            
            if steps_taken % 100 == 0:
                print(f"Moving to X-MIN: {steps_taken} steps, position: {motor_control.current_x:.2f}mm")
        
        if steps_taken >= max_steps:
            print("ERROR: X-axis failed to find MIN limit within safety limit")
            return False
        
        print(f"X axis reached MIN position at {motor_control.current_x:.2f}mm")
        
        # Back off from X-MIN
        print("Backing off from X-MIN...")
        
        # Direction: away from MIN (HIGH)
        GPIO.output(X_DIR_PIN, GPIO.HIGH)
        time.sleep(0.2)  # Longer direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_X)):
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_x += 1 / STEPS_PER_MM_X
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off from MIN: {i} steps, position: {motor_control.current_x:.2f}mm")
    
    # Store the X-MIN position (with backoff already applied)
    x_min_position = motor_control.current_x
    print(f"X-MIN position (with backoff): {x_min_position:.2f}mm")
    
    # Add a pause before changing direction for next phase
    print("Pausing before moving to X-MAX...")
    time.sleep(1.0)  # 1 second pause
    
    # STEP 2: Now go to X-MAX to determine the maximum travel range
    print("\nSTEP 2: Moving to X-MAX position...")
    
    # Check if already at X-MAX limit switch
    if check_limit_switch(X_MAX_LIMIT_PIN):
        print("X axis already at MAX limit position")
        # Back off slightly
        print("Backing off from X-MAX...")
        
        # Direction: away from MAX (LOW)
        GPIO.output(X_DIR_PIN, GPIO.LOW)
        time.sleep(0.2)  # Longer direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_X)):
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_x -= 1 / STEPS_PER_MM_X
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off from MAX: {i} steps, position: {motor_control.current_x:.2f}mm")
    else:
        # Move X toward MAX until limit switch is triggered or safety limit reached
        print("Moving toward X-MAX...")
        
        # Direction: toward MAX (HIGH) - explicit setting
        GPIO.output(X_DIR_PIN, GPIO.HIGH)
        time.sleep(0.2)  # Longer direction signal settle time
        
        steps_taken = 0
        max_steps = int(MAX_HOMING_DISTANCE * STEPS_PER_MM_X)
        
        # Fast approach to X-MAX
        while steps_taken < max_steps:
            # Check limit switch at beginning of each loop iteration
            if check_limit_switch(X_MAX_LIMIT_PIN):
                print(f"X-MAX limit switch triggered after {steps_taken} steps")
                time.sleep(0.05)  # Longer delay to ensure signal is stable
                # Double-check to avoid false triggers
                if check_limit_switch(X_MAX_LIMIT_PIN):
                    break
                
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            steps_taken += 1
            
            # Update position tracking
            motor_control.current_x += 1 / STEPS_PER_MM_X
            
            if steps_taken % 100 == 0:
                print(f"Moving to X-MAX: {steps_taken} steps, position: {motor_control.current_x:.2f}mm")
        
        if steps_taken >= max_steps:
            print("ERROR: X-axis failed to find MAX limit within safety limit")
            return False
        
        print(f"X axis reached MAX position at {motor_control.current_x:.2f}mm")
        
        # Back off from X-MAX
        print("Backing off from X-MAX...")
        
        # Direction: away from MAX (LOW)
        GPIO.output(X_DIR_PIN, GPIO.LOW)
        time.sleep(0.2)  # Longer direction signal settle time
        
        for i in range(int(HOMING_BACKOFF * STEPS_PER_MM_X)):
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_x -= 1 / STEPS_PER_MM_X
            
            if i % 100 == 0 and i > 0:
                print(f"Backing off from MAX: {i} steps, position: {motor_control.current_x:.2f}mm")
    
    # Store the X-MAX position (with backoff already applied)
    x_max_position = motor_control.current_x
    print(f"X-MAX position (with backoff): {x_max_position:.2f}mm")
    
    # Calculate total X travel range
    x_travel_range = abs(x_max_position - x_min_position)
    print(f"Total X travel range: {x_travel_range:.2f}mm")
    
    # STEP 3: Set position to zero at MIN and move to center
    print("\nSTEP 3: Setting X=0 at MIN and moving to center position...")
    
    # We're currently at x_max_position (backed off from MAX)
    # Set our current position to be equal to the total travel range
    motor_control.current_x = x_travel_range
    
    # Calculate steps to move to center position
    center_position = x_travel_range / 2
    print(f"X center position calculated at {center_position:.2f}mm")
    
    # Calculate number of steps needed to reach center from current position
    steps_to_center = int(abs(motor_control.current_x - center_position) * STEPS_PER_MM_X)
    
    if motor_control.current_x > center_position:
        # Need to move toward MIN (LOW direction)
        print(f"Moving {steps_to_center} steps toward center (using LOW direction)...")
        
        GPIO.output(X_DIR_PIN, GPIO.LOW)
        time.sleep(0.2)  # Direction signal settle time
        
        for i in range(steps_to_center):
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            
            motor_control.current_x -= 1 / STEPS_PER_MM_X
            
            if i % 100 == 0 and i > 0:
                print(f"Moving to center: {i}/{steps_to_center} steps, position: {motor_control.current_x:.2f}mm")
    else:
        # Need to move toward MAX (HIGH direction)
        print(f"Moving {steps_to_center} steps toward center (using HIGH direction)...")
        
        GPIO.output(X_DIR_PIN, GPIO.HIGH)
        time.sleep(0.2)  # Direction signal settle time
        
        for i in range(steps_to_center):
            GPIO.output(X_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(X_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            
            motor_control.current_x += 1 / STEPS_PER_MM_X
            
            if i % 100 == 0 and i > 0:
                print(f"Moving to center: {i}/{steps_to_center} steps, position: {motor_control.current_x:.2f}mm")
    
    print(f"X homing complete. Current position: {motor_control.current_x:.2f}mm")
    motor_control.x_min_position = x_min_position
    motor_control.x_max_position = x_max_position
    
    return True

def move_y_to_max(motor_control):
    """
    Move Y-axis toward MAX limit switch
    
    Args:
        motor_control: Reference to the motor_control module to update position
    """
    print("Moving Y-axis to MAX position...")
    
    # First check if already at the max limit switch
    if check_limit_switch(Y_MAX_LIMIT_PIN):
        print("Y axis already at max limit position")
        
        # Back off slightly
        for _ in range(int(HOMING_BACKOFF * STEPS_PER_MM_Y)):
            GPIO.output(Y1_DIR_PIN, GPIO.HIGH)  # Direction: away from MAX
            GPIO.output(Y2_DIR_PIN, GPIO.HIGH)
            
            GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(Y2_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_y += 1 / STEPS_PER_MM_Y
            
        print(f"Backed off Y-axis to position: {motor_control.current_y:.2f}mm")
        return True
    
    # Move Y toward MAX until limit switch is triggered or safety limit reached
    steps_taken = 0
    max_steps = int(MAX_HOMING_DISTANCE * STEPS_PER_MM_Y)
    
    print("Moving toward Y MAX limit switch...")
    
    # IMPORTANT: Direction is LOW for moving toward Y_MAX based on your feedback
    while not check_limit_switch(Y_MAX_LIMIT_PIN) and steps_taken < max_steps:
        # Direction is LOW to move toward MAX
        GPIO.output(Y1_DIR_PIN, GPIO.LOW)
        GPIO.output(Y2_DIR_PIN, GPIO.LOW)
        
        GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(HOMING_SPEED_FAST)
        GPIO.output(Y1_STEP_PIN, GPIO.LOW)
        GPIO.output(Y2_STEP_PIN, GPIO.LOW)
        time.sleep(HOMING_SPEED_FAST)
        
        steps_taken += 1
        
        # Update position tracking (note: we use -= because direction is reversed)
        motor_control.current_y -= 1 / STEPS_PER_MM_Y
        
        # Print progress occasionally
        if steps_taken % 100 == 0:
            print(f"Y moving to max: {steps_taken} steps, position: {motor_control.current_y:.2f}mm")
            # Check if limit switch is active
            if check_limit_switch(Y_MAX_LIMIT_PIN):
                print("Y MAX limit switch triggered")
    
    # If we hit the safety limit without finding max, report error
    if steps_taken >= max_steps:
        print("ERROR: Y-axis failed to find max limit within safety limit")
        return False
        
    print(f"Y axis reached MAX position at {motor_control.current_y:.2f}mm")
    
    # Back off slightly
    print("Backing off from Y MAX limit...")
    for _ in range(int(HOMING_BACKOFF * STEPS_PER_MM_Y)):
        GPIO.output(Y1_DIR_PIN, GPIO.HIGH)  # Direction: away from MAX
        GPIO.output(Y2_DIR_PIN, GPIO.HIGH)
        
        GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(HOMING_SPEED_SLOW)
        GPIO.output(Y1_STEP_PIN, GPIO.LOW)
        GPIO.output(Y2_STEP_PIN, GPIO.LOW)
        time.sleep(HOMING_SPEED_SLOW)
        
        # Update position tracking
        motor_control.current_y += 1 / STEPS_PER_MM_Y
    
    print(f"Y axis backed off to position {motor_control.current_y:.2f}mm")
    return True

def home_y_axes(motor_control):
    """
    Home both Y motors by first finding MAX, then MIN, then positioning halfway between
    
    Args:
        motor_control: Reference to the motor_control module to update position
    """
    print("Homing Y axes...")
    
    # Step 1: First go to Y-MAX to establish the maximum boundary
    print("Step 1: Moving to Y-MAX position...")
    
    # Check if already at Y-MAX limit switch
    if check_limit_switch(Y_MAX_LIMIT_PIN):
        print("Y axis already at MAX limit position")
        # Back off slightly
        for _ in range(int(HOMING_BACKOFF * STEPS_PER_MM_Y)):
            GPIO.output(Y1_DIR_PIN, GPIO.HIGH)  # Direction: away from MAX
            GPIO.output(Y2_DIR_PIN, GPIO.HIGH)
            
            GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(Y2_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_y += 1 / STEPS_PER_MM_Y
    else:
        # Move Y toward MAX until limit switch is triggered or safety limit reached
        steps_taken = 0
        max_steps = int(MAX_HOMING_DISTANCE * STEPS_PER_MM_Y)
        
        # Fast approach to Y-MAX
        while not check_limit_switch(Y_MAX_LIMIT_PIN) and steps_taken < max_steps:
            # Direction is LOW to move toward MAX
            GPIO.output(Y1_DIR_PIN, GPIO.LOW)
            GPIO.output(Y2_DIR_PIN, GPIO.LOW)
            
            GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(Y2_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            
            steps_taken += 1
            
            # Update position tracking
            motor_control.current_y -= 1 / STEPS_PER_MM_Y
            
            # Print progress occasionally
            if steps_taken % 100 == 0:
                print(f"Y moving to MAX: {steps_taken} steps, position: {motor_control.current_y:.2f}mm")
        
        # If we hit the safety limit without finding MAX, report error
        if steps_taken >= max_steps:
            print("ERROR: Y-axis failed to find MAX limit within safety limit")
            return False
            
        print(f"Y axis reached MAX position at {motor_control.current_y:.2f}mm")
        
        # Back off slightly from Y-MAX
        for _ in range(int(HOMING_BACKOFF * STEPS_PER_MM_Y)):
            GPIO.output(Y1_DIR_PIN, GPIO.HIGH)  # Direction: away from MAX
            GPIO.output(Y2_DIR_PIN, GPIO.HIGH)
            
            GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(Y2_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_y += 1 / STEPS_PER_MM_Y
    
    # Store the Y-MAX position (with backoff already applied)
    y_max_position = motor_control.current_y
    print(f"Y-MAX position (with backoff): {y_max_position:.2f}mm")
    
    # Step 2: Now go to Y-MIN
    print("\nStep 2: Moving to Y-MIN position...")
    
    # First check if Y is already at the MIN limit switch
    if check_limit_switch(Y_MIN_LIMIT_PIN):
        print("Y axis already at MIN limit position")
        # Back off slightly
        for _ in range(int(HOMING_BACKOFF * STEPS_PER_MM_Y)):
            GPIO.output(Y1_DIR_PIN, GPIO.HIGH)  # Direction: away from MIN
            GPIO.output(Y2_DIR_PIN, GPIO.HIGH)
            
            GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(Y2_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking
            motor_control.current_y += 1 / STEPS_PER_MM_Y
    else:
        # Move Y toward MIN until limit switch is triggered or safety limit reached
        steps_taken = 0
        max_steps = int(MAX_HOMING_DISTANCE * STEPS_PER_MM_Y)
        
        # Fast approach phase - IMPORTANT: Using HIGH direction to move toward MIN
        # This is the opposite of what we used for MAX
        print("Fast approach to Y-MIN - Moving in opposite direction from MAX")
        
        while not check_limit_switch(Y_MIN_LIMIT_PIN) and steps_taken < max_steps:
            # Direction is HIGH to move toward MIN (opposite from MAX direction)
            GPIO.output(Y1_DIR_PIN, GPIO.HIGH)
            GPIO.output(Y2_DIR_PIN, GPIO.HIGH)
            
            GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_FAST)
            GPIO.output(Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(Y2_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_FAST)
            
            steps_taken += 1
            
            # Update position tracking - Note we're ADDING here since we're using HIGH
            motor_control.current_y += 1 / STEPS_PER_MM_Y
            
            # Print progress occasionally
            if steps_taken % 100 == 0:
                print(f"Y moving to MIN: {steps_taken} steps, position: {motor_control.current_y:.2f}mm")
        
        # If we didn't find MIN within the safety limit, report error
        if steps_taken >= max_steps:
            print("ERROR: Y-axis failed to find MIN limit within safety limit")
            return False
        
        print(f"Y axis reached MIN position at {motor_control.current_y:.2f}mm")
        
        # Back off slightly from Y-MIN - Using LOW direction to back off from MIN
        for _ in range(int(HOMING_BACKOFF * STEPS_PER_MM_Y)):
            GPIO.output(Y1_DIR_PIN, GPIO.LOW)  # Direction: away from MIN (opposite from approach)
            GPIO.output(Y2_DIR_PIN, GPIO.LOW)
            
            GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(HOMING_SPEED_SLOW)
            GPIO.output(Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(Y2_STEP_PIN, GPIO.LOW)
            time.sleep(HOMING_SPEED_SLOW)
            
            # Update position tracking - Subtracting here since we're using LOW
            motor_control.current_y -= 1 / STEPS_PER_MM_Y
    
    # Store the Y-MIN position (with backoff already applied)
    y_min_position = motor_control.current_y
    print(f"Y-MIN position (with backoff): {y_min_position:.2f}mm")
    
    # Calculate total Y travel range
    # We need the absolute distance between MAX and MIN positions
    y_travel_range = abs(y_max_position - y_min_position)
    print(f"Total Y travel range: {y_travel_range:.2f}mm")
    
    motor_control.y_min_position = min(y_min_position, y_max_position)
    motor_control.y_max_position = max(y_min_position, y_max_position)
    
    # Step 3: Set current position as Y-MIN reference point
    motor_control.current_y = 0  # This is our Y-MIN reference
    print(f"Y-MIN is now zero reference. Y-MAX is now at {y_travel_range:.2f}mm")
    
    # Step 4: Move to the center position between MIN and MAX
    y_center_position = y_travel_range / 2
    print(f"Moving to center position at Y={y_center_position:.2f}mm")
    
    # Calculate steps to move to center
    steps_to_center = int(y_center_position * STEPS_PER_MM_Y)
    
    # IMPORTANT: Move to center position - using LOW direction to move toward center
    # This is the critical fix - we need to use the LOW direction, not HIGH
    print(f"Taking {steps_to_center} steps toward center (using LOW direction)...")
    for _ in range(steps_to_center):
        GPIO.output(Y1_DIR_PIN, GPIO.LOW)  # Direction: toward center (LOW direction)
        GPIO.output(Y2_DIR_PIN, GPIO.LOW)
        
        GPIO.output(Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(HOMING_SPEED_FAST)
        GPIO.output(Y1_STEP_PIN, GPIO.LOW)
        GPIO.output(Y2_STEP_PIN, GPIO.LOW)
        time.sleep(HOMING_SPEED_FAST)
        
        # Update position tracking - we're using LOW so we SUBTRACT
        motor_control.current_y -= 1 / STEPS_PER_MM_Y
        
        # Print progress occasionally
        if _ % 500 == 0 and _ > 0:
            print(f"Moving to center... {_}/{steps_to_center} steps, position: {motor_control.current_y:.2f}mm")
    
    print(f"Y homing complete. Current position: {motor_control.current_y:.2f}mm")
    print(f"Y-axis should now be centered at approximately half the total travel range.")


    
    return True

# Export the limit switch pin definitions for use in movement functions
def get_limit_pins():
    """Return all limit switch pin definitions"""
    return {
        'x_min': X_MIN_LIMIT_PIN,
        'x_max': X_MAX_LIMIT_PIN,
        'y_min': Y_MIN_LIMIT_PIN,
        'y_max': Y_MAX_LIMIT_PIN,
        'z_min': Z_MIN_LIMIT_PIN,
        'z_max': Z_MAX_LIMIT_PIN
    }

Z_MIN = 0.0
Z_MAX = 0.0

def get_z_limits(mc=None):
    global Z_MIN, Z_MAX
    Z_MIN = mc.Z_RELEASE_POSITION
    Z_MAX = mc.Z_MAX_HEIGHT
    return Z_MIN, Z_MAX