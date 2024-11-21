import cv2
from datetime import datetime
import os


def record():
    # Ensure recordings directory exists
    os.makedirs('recordings', exist_ok=True)

    # Open camera capture
    cap = cv2.VideoCapture(0)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    # Video writer configuration
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_path = f'recordings/{datetime.now().strftime("%H-%M-%S")}.avi'
    storage = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

    try:
        while True:
            # Read frame from camera
            ret, frame = cap.read()

            if not ret:
                print("Failed to grab frame")
                break

            # Add timestamp to frame
            cv2.putText(frame,
                        datetime.now().strftime("%H:%M:%S"),
                        (10, 30),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.6,
                        (225, 0, 225),
                        2)

            # Write frame to video
            storage.write(frame)

            # Display frame
            cv2.imshow('Press ESC to stop', frame)

            # Check for ESC key
            key = cv2.waitKey(1)
            if key == 27:  # ESC key
                break

    finally:
        # Cleanup resources
        cap.release()
        storage.release()
        cv2.destroyAllWindows()