import cv2
import sys
import numpy as np
import platform
import time

def check_opencv_build():
    """Check OpenCV build information and capabilities"""
    print("\n=== OpenCV Build Information ===")
    print(f"OpenCV Version: {cv2.__version__}")
    
    build_info = cv2.getBuildInformation()
    
    print(f"\nPlatform: {platform.system()} {platform.release()}")
    print(f"Python Version: {platform.python_version()}")
    
    # Check for video capture capabilities
    print("\n=== Video Capture Backend Information ===")
    backend_types = [
        cv2.CAP_DSHOW,     # DirectShow (preferred on Windows)
        cv2.CAP_MSMF,      # Microsoft Media Foundation
        cv2.CAP_V4L2,      # Video for Linux
        cv2.CAP_ANY        # Auto-detect
    ]
    
    backend_names = {
        cv2.CAP_DSHOW: "DirectShow",
        cv2.CAP_MSMF: "Microsoft Media Foundation",
        cv2.CAP_V4L2: "Video4Linux2",
        cv2.CAP_ANY: "Automatic"
    }
    
    print("Available backends:")
    for backend in backend_types:
        try:
            name = backend_names.get(backend, f"Backend {backend}")
            print(f"  - {name}")
        except:
            pass

def test_camera_with_backend(index, backend):
    """Test camera connection with specific backend"""
    backend_name = {
        cv2.CAP_DSHOW: "DirectShow",
        cv2.CAP_MSMF: "Microsoft Media Foundation",
        cv2.CAP_ANY: "Automatic"
    }.get(backend, f"Backend {backend}")
    
    print(f"\nTesting camera {index} with {backend_name}...")
    
    try:
        cap = cv2.VideoCapture(index + backend)
        
        if not cap.isOpened():
            print(f"Failed to open camera with {backend_name}")
            return False
        
        # Try reading a frame
        ret, frame = cap.read()
        
        if not ret:
            print(f"Failed to read frame with {backend_name}")
            cap.release()
            return False
        
        # Get camera properties
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Success! Camera opened with {backend_name}")
        print(f"  Resolution: {int(width)}x{int(height)}")
        print(f"  FPS: {fps}")
        
        # Display a few frames
        print("Displaying camera feed (press 'q' to quit)...")
        
        start_time = time.time()
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame capture failed")
                break
            
            frame_count += 1
            current_time = time.time()
            if current_time - start_time >= 1.0:
                fps_actual = frame_count / (current_time - start_time)
                frame_count = 0
                start_time = current_time
                cv2.putText(frame, f"FPS: {fps_actual:.2f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow(f"Camera {index} - {backend_name}", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        cap.release()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def enumerate_cameras():
    """Try to enumerate cameras using Windows-specific methods"""
    print("\n=== Enumerating Cameras ===")
    
    try:
        # Try using DirectShow backend which is often better on Windows
        working_cameras = []
        
        # Test multiple cameras with DirectShow
        print("Testing with DirectShow backend...")
        for i in range(10):
            cap = cv2.VideoCapture(i + cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    working_cameras.append(f"Index {i} (DirectShow)")
                    print(f"Found camera at index {i} with DirectShow")
                cap.release()
        
        # Test with Microsoft Media Foundation
        print("\nTesting with Microsoft Media Foundation backend...")
        for i in range(10):
            cap = cv2.VideoCapture(i + cv2.CAP_MSMF)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    working_cameras.append(f"Index {i} (MSMF)")
                    print(f"Found camera at index {i} with MSMF")
                cap.release()
        
        if working_cameras:
            print(f"\nFound {len(working_cameras)} working camera(s):")
            for cam in working_cameras:
                print(f"  - {cam}")
        else:
            print("\nNo working cameras found.")
            
    except Exception as e:
        print(f"Error during enumeration: {e}")

def test_with_alternative_libraries():
    """Suggest alternative libraries for testing"""
    print("\n=== Alternative Libraries ===")
    print("If OpenCV doesn't work, try these alternatives:")
    print("1. PyCapture2 for FLIR/Point Grey cameras")
    print("2. Pillow (PIL) with ImageGrab for screen capture")
    print("3. Windows Media Foundation directly")
    print("4. pygame for basic camera access")
    
    print("\nYou can install them with:")
    print("pip install pillow pygame")

def main():
    print("=== Advanced Camera Diagnostics ===")
    
    # Check OpenCV build information
    check_opencv_build()
    
    # Enumerate cameras
    enumerate_cameras()
    
    # Test with different backends
    print("\n=== Testing Different Backends ===")
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    
    for index in range(3):  # Test first 3 indices
        for backend in backends:
            if test_camera_with_backend(index, backend):
                print(f"Camera {index} works with backend {backend}")
                return  # Exit if we find a working configuration
    
    # If nothing works, suggest alternatives
    test_with_alternative_libraries()
    
    print("\n=== Troubleshooting Tips ===")
    print("1. Ensure camera drivers are up to date")
    print("2. Check Device Manager for camera status")
    print("3. Try uninstalling and reinstalling OpenCV with:")
    print("   pip uninstall opencv-python")
    print("   pip install opencv-python-headless")
    print("   pip install opencv-contrib-python")
    print("4. Check if other apps (Skype, Teams) can access the camera")
    print("5. Restart your computer")
    print("6. Check if antivirus is blocking camera access")

if __name__ == "__main__":
    main()