import time
import Adafruit_BBIO.GPIO as GPIO
import motor_control as mc
import home_cnc as hs

# Increase the safety limit
hs.MAX_HOMING_DISTANCE = 2000  # Very large value to ensure we don't time out

# Increase the backoff distance
hs.HOMING_BACKOFF = 10  # Increased from 5mm to 10mm for more clearance from limits

def setup():
    """Initialize the system for testing"""
    print("Initializing for homing test...")
    
    # Initialize motor control
    mc.init_motors()
    
    # Initialize limit switches
    hs.init_limit_switches()
    
    # Connect limit switch checking to motor control
    mc.set_limit_check_function(check_limit)
    
    print(f"Initialization complete. Safety limit: {hs.MAX_HOMING_DISTANCE}mm, Backoff: {hs.HOMING_BACKOFF}mm")

def check_limit(limit_name):
    """Check a specific limit switch"""
    limits = hs.check_axis_limits()
    return limits.get(limit_name, False)

def test_x_homing():
    """Test X-axis homing only"""
    print("\nTesting X-axis homing...")
    result = hs.home_x_axis(mc)
    
    if result:
        print("X homing successful!")
    else:
        print("X homing failed!")
    
    # Show current position
    x, y, z = mc.get_current_position()
    print(f"Current X position: {x:.2f}mm")

def test_y_homing():
    """Test Y-axis homing only"""
    print("\nTesting Y-axis homing...")
    result = hs.home_y_axes(mc)
    
    if result:
        print("Y homing successful!")
    else:
        print("Y homing failed!")
    
    # Show current position
    x, y, z = mc.get_current_position()
    print(f"Current Y position: {y:.2f}mm")

def test_y_max():
    """Test moving Y-axis to max limit"""
    print("\nTesting Y-axis to MAX limit...")
    result = hs.move_y_to_max(mc)
    
    if result:
        print("Y-MAX movement successful!")
    else:
        print("Y-MAX movement failed!")
    
    # Show current position
    x, y, z = mc.get_current_position()
    print(f"Current Y position: {y:.2f}mm")

def test_z_homing():
    """Test Z-axis homing only"""
    print("\nTesting Z-axis homing...")
    result = hs.home_z_axis(mc)
    
    if result:
        print(f"Z homing successful!")
        print(f"Z_MAX_HEIGHT set to: {mc.Z_MAX_HEIGHT:.2f}mm")
        print(f"Z_RELEASE_POSITION set to: {mc.Z_RELEASE_POSITION:.2f}mm")
    else:
        print("Z homing failed!")
    
    # Show current position
    x, y, z = mc.get_current_position()
    print(f"Current Z position: {z:.2f}mm")

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

def test_all_axes_individually():
    """Test homing for all axes one by one"""
    print("\nTesting all axes individually...")
    
    # First Z for safety
    test_z_homing()
    
    # Then X
    test_x_homing()
    
    # Then Y
    test_y_homing()
    
    # Finally test Y to MAX
    test_y_max()
    
    print("Individual axis tests complete")

def test_all_homing():
    """Test complete homing sequence for all axes"""
    print("\nTesting complete homing sequence...")
    hs.home_cnc(mc)
    
    # Report final positions
    x, y, z = mc.get_current_position()
    print(f"Final positions after homing:")
    print(f"  X: {x:.2f}mm")
    print(f"  Y: {y:.2f}mm")
    print(f"  Z: {z:.2f}mm")

def main():
    """Main test function"""
    try:
        # Setup system
        setup()
        
        # Test menu
        while True:
            print("\nCNC Homing Test Menu:")
            print("1. Check all limit switches")
            print("2. Test X-axis homing")
            print("3. Test Y-axis homing")
            print("4. Test Y-axis to MAX")
            print("5. Test Z-axis homing")
            print("6. Test all axes individually")
            print("7. Test all axes homing sequence")
            print("8. Change backoff distance")
            print("9. Change safety limit")
            print("10. Exit")
            
            choice = input("Enter choice (1-10): ")
            
            if choice == "1":
                check_all_limits()
            elif choice == "2":
                test_x_homing()
            elif choice == "3":
                test_y_homing()
            elif choice == "4":
                test_y_max()
            elif choice == "5":
                test_z_homing()
            elif choice == "6":
                test_all_axes_individually()
            elif choice == "7":
                test_all_homing()
            elif choice == "8":
                try:
                    new_backoff = float(input("Enter new backoff distance in mm (e.g. 10): "))
                    hs.HOMING_BACKOFF = new_backoff
                    print(f"Backoff distance updated to {hs.HOMING_BACKOFF} mm")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            elif choice == "9":
                try:
                    new_limit = float(input("Enter new safety limit in mm (e.g. 2000): "))
                    hs.MAX_HOMING_DISTANCE = new_limit
                    print(f"Safety limit updated to {hs.MAX_HOMING_DISTANCE} mm")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            elif choice == "10":
                print("Exiting test program...")
                break
            else:
                print("Invalid choice. Please enter 1-10.")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        mc.cleanup()
        print("GPIO pins cleaned up")

if __name__ == "__main__":
    main()