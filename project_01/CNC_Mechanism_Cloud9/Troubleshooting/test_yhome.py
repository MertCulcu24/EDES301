import time
import Adafruit_BBIO.GPIO as GPIO
import motor_control as mc
import home_cnc as hs

# Increase the safety limit
hs.MAX_HOMING_DISTANCE = 2000  # Very large value to ensure we don't time out

def setup():
    """Initialize the system for testing"""
    print("Initializing for Y-MAX limit switch test...")
    
    # Initialize motor control
    mc.init_motors()
    
    # Initialize limit switches
    hs.init_limit_switches()
    
    # Connect limit switch checking to motor control
    mc.set_limit_check_function(check_limit)
    
    print(f"Initialization complete. Safety limit set to {hs.MAX_HOMING_DISTANCE} mm")

def check_limit(limit_name):
    """Check a specific limit switch"""
    limits = hs.check_axis_limits()
    return limits.get(limit_name, False)

def test_y_max_limit():
    """Test the Y-MAX limit switch specifically"""
    print("\nTesting Y-MAX limit switch...")
    
    # First check if Y-MAX is already triggered
    if check_limit('y_max'):
        print("Y-MAX switch already triggered!")
        return
    
    print("Moving Y-axis toward MAX switch (using LOW direction)...")
    
    # Track steps
    steps_taken = 0
    
    # Run motors toward Y-MAX until switch is triggered
    # IMPORTANT: Using LOW direction to move toward Y-MAX based on your feedback
    while not check_limit('y_max') and steps_taken < hs.MAX_HOMING_DISTANCE * hs.STEPS_PER_MM_Y:
        # Set direction to LOW (now heading toward MAX based on feedback)
        GPIO.output(mc.Y1_DIR_PIN, GPIO.LOW)
        GPIO.output(mc.Y2_DIR_PIN, GPIO.LOW)
        
        # Pulse both Y motors
        GPIO.output(mc.Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(mc.Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(hs.HOMING_SPEED_FAST)
        GPIO.output(mc.Y1_STEP_PIN, GPIO.LOW)
        GPIO.output(mc.Y2_STEP_PIN, GPIO.LOW)
        time.sleep(hs.HOMING_SPEED_FAST)
        
        steps_taken += 1
        
        # Update tracking position - adjusted for direction
        mc.current_y -= 1 / hs.STEPS_PER_MM_Y  # Using -= since direction is reversed
        
        # Print progress occasionally
        if steps_taken % 1000 == 0:
            print(f"Y-axis moved {steps_taken} steps, position: {mc.current_y:.2f}mm")
            print(f"Y-MAX switch status: {'TRIGGERED' if check_limit('y_max') else 'Open'}")
    
    if check_limit('y_max'):
        print(f"Y-MAX switch triggered after {steps_taken} steps!")
        print(f"Final Y position: {mc.current_y:.2f}mm")
    else:
        print(f"Y-MAX switch not triggered after {steps_taken} steps.")
        print(f"Reached safety limit. Final Y position: {mc.current_y:.2f}mm")
    
    # Now back off from the limit
    if check_limit('y_max'):
        print("Backing off from Y-MAX limit...")
        backoff_steps = int(hs.HOMING_BACKOFF * hs.STEPS_PER_MM_Y)
        
        for _ in range(backoff_steps):
            GPIO.output(mc.Y1_DIR_PIN, GPIO.HIGH)  # Now using HIGH to move away from MAX
            GPIO.output(mc.Y2_DIR_PIN, GPIO.HIGH)
            
            GPIO.output(mc.Y1_STEP_PIN, GPIO.HIGH)
            GPIO.output(mc.Y2_STEP_PIN, GPIO.HIGH)
            time.sleep(hs.HOMING_SPEED_SLOW)
            GPIO.output(mc.Y1_STEP_PIN, GPIO.LOW)
            GPIO.output(mc.Y2_STEP_PIN, GPIO.LOW)
            time.sleep(hs.HOMING_SPEED_SLOW)
            
            # Update tracking position
            mc.current_y += 1 / hs.STEPS_PER_MM_Y  # Using += since direction is HIGH
        
        print(f"Backed off to Y position: {mc.current_y:.2f}mm")
        print(f"Y-MAX switch now: {'TRIGGERED' if check_limit('y_max') else 'Open'}")

def check_all_limits():
    """Check and display the status of all limit switches"""
    print("\nChecking all limit switches:")
    limits = hs.check_axis_limits()
    
    print("X-axis limits:")
    print(f"  Min (home): {'TRIGGERED' if limits['x_min'] else 'Open'}")
    print(f"  Max: {'TRIGGERED' if limits['x_max'] else 'Open'}")
    
    print("Y-axis limits:")
    print(f"  Min (home): {'TRIGGERED' if limits['y_min'] else 'Open'}")
    print(f"  Max: {'TRIGGERED' if limits['y_max'] else 'Open'}")
    
    print("Z-axis limits:")
    print(f"  Min (home): {'TRIGGERED' if limits['z_min'] else 'Open'}")
    print(f"  Max: {'TRIGGERED' if limits['z_max'] else 'Open'}")

def toggle_y_direction():
    """Test function to toggle Y direction to determine which way is toward Y_MAX"""
    print("\nToggling Y direction test...")
    
    # First direction
    print("Testing Y direction 1 (DIR=HIGH)...")
    GPIO.output(mc.Y1_DIR_PIN, GPIO.HIGH)
    GPIO.output(mc.Y2_DIR_PIN, GPIO.HIGH)
    
    # Move 1000 steps
    for _ in range(1000):
        GPIO.output(mc.Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(mc.Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(hs.HOMING_SPEED_FAST)
        GPIO.output(mc.Y1_STEP_PIN, GPIO.LOW)
        GPIO.output(mc.Y2_STEP_PIN, GPIO.LOW)
        time.sleep(hs.HOMING_SPEED_FAST)
    
    # Check Y_MAX status
    print(f"After 1000 steps DIR=HIGH, Y-MAX switch: {'TRIGGERED' if check_limit('y_max') else 'Open'}")
    
    # Pause
    time.sleep(2)
    
    # Opposite direction
    print("Testing Y direction 2 (DIR=LOW)...")
    GPIO.output(mc.Y1_DIR_PIN, GPIO.LOW)
    GPIO.output(mc.Y2_DIR_PIN, GPIO.LOW)
    
    # Move 1000 steps
    for _ in range(1000):
        GPIO.output(mc.Y1_STEP_PIN, GPIO.HIGH)
        GPIO.output(mc.Y2_STEP_PIN, GPIO.HIGH)
        time.sleep(hs.HOMING_SPEED_FAST)
        GPIO.output(mc.Y1_STEP_PIN, GPIO.LOW)
        GPIO.output(mc.Y2_STEP_PIN, GPIO.LOW)
        time.sleep(hs.HOMING_SPEED_FAST)
    
    # Check Y_MAX status
    print(f"After 1000 steps DIR=LOW, Y-MAX switch: {'TRIGGERED' if check_limit('y_max') else 'Open'}")

def main():
    """Main test function"""
    try:
        # Setup system
        setup()
        
        # Test menu
        while True:
            print("\nY-MAX Limit Switch Test Menu:")
            print("1. Check all limit switches")
            print("2. Test Y-MAX limit switch")
            print("3. Toggle Y direction test")
            print("4. Exit")
            
            choice = input("Enter choice (1-4): ")
            
            if choice == "1":
                check_all_limits()
            elif choice == "2":
                test_y_max_limit()
            elif choice == "3":
                toggle_y_direction()
            elif choice == "4":
                print("Exiting test program...")
                break
            else:
                print("Invalid choice. Please enter 1-4.")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        mc.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()