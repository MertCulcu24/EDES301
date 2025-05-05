import Adafruit_BBIO.GPIO as GPIO
import time

# Z-Axis pins from your motor_control.py
Z_STEP_PIN = "P2_20"
Z_DIR_PIN = "P2_3"

# Step delay in seconds
STEP_DELAY = 0.0005

def setup():
    """Initialize pins"""
    # Setup Z motor control pins
    GPIO.setup(Z_STEP_PIN, GPIO.OUT)
    GPIO.setup(Z_DIR_PIN, GPIO.OUT)
    
    GPIO.output(Z_STEP_PIN, GPIO.LOW)
    GPIO.output(Z_DIR_PIN, GPIO.LOW)
    
    print("Z-axis pins initialized")

def move_z(steps, direction):
    """
    Move Z-axis a specific number of steps in a direction
    
    Args:
        steps: Number of steps to move
        direction: True for upward (HIGH), False for downward (LOW)
    """
    print(f"Moving Z-axis {'UP' if direction else 'DOWN'} for {steps} steps")
    
    # Set direction pin
    GPIO.output(Z_DIR_PIN, GPIO.HIGH if direction else GPIO.LOW)
    time.sleep(0.1)  # Direction signal settle time
    
    # Execute steps
    for i in range(steps):
        GPIO.output(Z_STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(Z_STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
        
        if i % 100 == 0:
            print(f"Step {i}/{steps}")

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
            print("\nZ-Axis Direction Test Menu:")
            print("1. Move Z DOWN (DIR=LOW)")
            print("2. Move Z UP (DIR=HIGH)")
            print("3. Exit")
            
            choice = input("Enter choice (1-3): ")
            
            if choice == "1":
                steps = int(input("Enter number of steps (100-1000): "))
                if steps < 100 or steps > 1000:
                    print("Invalid step count. Using 100 steps.")
                    steps = 100
                
                # Move Z DOWN with DIR=LOW
                move_z(steps, False)
                
            elif choice == "2":
                steps = int(input("Enter number of steps (100-1000): "))
                if steps < 100 or steps > 1000:
                    print("Invalid step count. Using 100 steps.")
                    steps = 100
                    
                # Move Z UP with DIR=HIGH
                move_z(steps, True)
                
            elif choice == "3":
                print("Exiting test program...")
                break
            else:
                print("Invalid choice. Please enter 1-3.")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        cleanup()

if __name__ == "__main__":
    main()