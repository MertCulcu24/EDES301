import Adafruit_BBIO.GPIO as GPIO
import time

# X-Axis pins from your motor_control.py
X_STEP_PIN = "P2_2"
X_DIR_PIN = "P2_4"
X_MIN_LIMIT_PIN = "P1_2"    # X-axis minimum (home) position limit switch
X_MAX_LIMIT_PIN = "P1_4"    # X-axis maximum position limit switch

# Step delay in seconds
STEP_DELAY = 0.001  # Slower for more precise control
STEPS_TO_MOVE = 200  # Number of steps for basic tests

def setup():
    """Initialize pins"""
    # Setup X motor control pins
    GPIO.setup(X_STEP_PIN, GPIO.OUT)
    GPIO.setup(X_DIR_PIN, GPIO.OUT)
    
    # Setup limit switches with pull-up resistors
    GPIO.setup(X_MIN_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(X_MAX_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Initialize to known state
    GPIO.output(X_STEP_PIN, GPIO.LOW)
    GPIO.output(X_DIR_PIN, GPIO.LOW)
    
    print("X-axis pins initialized")

def check_limit_switch(limit_pin):
    """Check if a limit switch is triggered"""
    # With pull-up resistors, switch is triggered when input reads LOW
    triggered = GPIO.input(limit_pin) == GPIO.LOW
    return triggered

def move_x(steps, direction_value):
    """
    Move X-axis a specific number of steps with a specific direction value
    
    Args:
        steps: Number of steps to move
        direction_value: GPIO.HIGH or GPIO.LOW
    """
    dir_text = "HIGH" if direction_value == GPIO.HIGH else "LOW"
    print(f"Moving X-axis with DIR={dir_text} for {steps} steps")
    
    # Set direction pin
    GPIO.output(X_DIR_PIN, direction_value)
    time.sleep(0.1)  # Direction signal settle time
    
    # Execute steps
    for i in range(steps):
        # Check limit switches
        x_min_triggered = check_limit_switch(X_MIN_LIMIT_PIN)
        x_max_triggered = check_limit_switch(X_MAX_LIMIT_PIN)
        
        if x_min_triggered or x_max_triggered:
            print(f"Limit switch triggered after {i} steps!")
            print(f"X-MIN: {'TRIGGERED' if x_min_triggered else 'open'}")
            print(f"X-MAX: {'TRIGGERED' if x_max_triggered else 'open'}")
            
            # Ask if we should continue
            if i > 10:  # Only ask if we've moved a significant distance
                response = input("Limit switch triggered. Continue? (y/n): ")
                if response.lower() != 'y':
                    break
        
        GPIO.output(X_STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(X_STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
        
        if i % 50 == 0:
            x_min_status = check_limit_switch(X_MIN_LIMIT_PIN)
            x_max_status = check_limit_switch(X_MAX_LIMIT_PIN)
            print(f"Step {i}/{steps}, X-MIN: {'TRIGGERED' if x_min_status else 'open'}, X-MAX: {'TRIGGERED' if x_max_status else 'open'}")

def move_to_min_limit():
    """Move X-axis toward MIN limit switch until triggered"""
    print("\nMoving toward X-MIN limit switch...")
    
    # First check if the limit switch is already triggered
    if check_limit_switch(X_MIN_LIMIT_PIN):
        print("X-MIN limit switch is already triggered!")
        return
    
    # Try with LOW direction first
    print("Trying with DIR=LOW...")
    
    # Set direction to LOW
    GPIO.output(X_DIR_PIN, GPIO.LOW)
    time.sleep(0.1)  # Direction signal settle time
    
    steps = 0
    max_steps = 1000  # Safety limit
    
    # Move until limit hit or max steps reached
    while steps < max_steps:
        # Check limit switch BEFORE moving
        if check_limit_switch(X_MIN_LIMIT_PIN):
            print(f"\nX-MIN LIMIT SWITCH TRIGGERED with DIR=LOW after {steps} steps!")
            print("This means LOW moves X toward MIN limit.")
            return True
            
        # Move one step
        GPIO.output(X_STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(X_STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
        
        steps += 1
        
        # Print status periodically
        if steps % 50 == 0:
            print(f"Step {steps}, X-MIN: {'TRIGGERED' if check_limit_switch(X_MIN_LIMIT_PIN) else 'open'}")
    
    # If we didn't hit the limit switch with LOW, try HIGH
    print("\nDidn't hit limit switch with DIR=LOW. Trying with DIR=HIGH...")
    
    # Set direction to HIGH
    GPIO.output(X_DIR_PIN, GPIO.HIGH)
    time.sleep(0.1)  # Direction signal settle time
    
    steps = 0
    
    # Move until limit hit or max steps reached
    while steps < max_steps:
        # Check limit switch BEFORE moving
        if check_limit_switch(X_MIN_LIMIT_PIN):
            print(f"\nX-MIN LIMIT SWITCH TRIGGERED with DIR=HIGH after {steps} steps!")
            print("This means HIGH moves X toward MIN limit.")
            return True
            
        # Move one step
        GPIO.output(X_STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(X_STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
        
        steps += 1
        
        # Print status periodically
        if steps % 50 == 0:
            print(f"Step {steps}, X-MIN: {'TRIGGERED' if check_limit_switch(X_MIN_LIMIT_PIN) else 'open'}")
    
    print("Didn't hit X-MIN limit switch in either direction after 2000 total steps.")
    return False

def test_limit_switch_response():
    """Test how the limit switches respond to being triggered"""
    print("\nTesting limit switch response...")
    
    print("Please manually trigger and release the X-MIN limit switch.")
    print("Monitoring for 10 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 10:
        x_min_status = check_limit_switch(X_MIN_LIMIT_PIN)
        x_max_status = check_limit_switch(X_MAX_LIMIT_PIN)
        
        status_text = f"X-MIN: {'TRIGGERED' if x_min_status else 'open'}, X-MAX: {'TRIGGERED' if x_max_status else 'open'}"
        print(status_text, end="\r")
        time.sleep(0.1)
    
    print("\nTest complete.")

def cleanup():
    """Clean up GPIO pins"""
    GPIO.cleanup()
    print("GPIO pins cleaned up")

def main():
    """Main test function"""
    try:
        # Initialize pins
        setup()
        
        # Test menu
        while True:
            print("\nX-Axis Test Menu:")
            print("1. Move X with DIR=LOW")
            print("2. Move X with DIR=HIGH")
            print("3. Find X-MIN limit direction")
            print("4. Test limit switch response")
            print("5. Exit")
            
            choice = input("Enter choice (1-5): ")
            
            if choice == "1":
                steps = int(input("Enter number of steps (50-500): ") or "200")
                steps = max(50, min(500, steps))  # Limit to 50-500 range
                move_x(steps, GPIO.LOW)
            elif choice == "2":
                steps = int(input("Enter number of steps (50-500): ") or "200")
                steps = max(50, min(500, steps))  # Limit to 50-500 range
                move_x(steps, GPIO.HIGH)
            elif choice == "3":
                move_to_min_limit()
            elif choice == "4":
                test_limit_switch_response()
            elif choice == "5":
                print("Exiting test program...")
                break
            else:
                print("Invalid choice. Please enter 1-5.")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        cleanup()

if __name__ == "__main__":
    main()