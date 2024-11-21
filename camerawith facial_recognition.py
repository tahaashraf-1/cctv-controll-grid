import cv2
import mediapipe as mp
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

# Initialize MediaPipe modules
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Set up GUI
root = Tk()
guiFrame = ttk.Frame(root, padding=10)
guiFrame.grid()

controlFrame = ttk.Frame(guiFrame, padding=10)
controlFrame.grid(column=0, row=0)

b1 = BooleanVar()
cb1 = ttk.Checkbutton(controlFrame, text='Face Bbox', variable=b1)
cb1.grid(column=0, row=0, padx=10)

b2 = BooleanVar()
cb2 = ttk.Checkbutton(controlFrame, text='Body Pose', variable=b2)
cb2.grid(column=1, row=0, padx=10)

b3 = BooleanVar()
cb3 = ttk.Checkbutton(controlFrame, text='Hands', variable=b3)
cb3.grid(column=2, row=0, padx=10)

def quitGUI():
    cam.release()
    root.destroy()

buttonQuit = ttk.Button(controlFrame, text='Quit', command=quitGUI)
buttonQuit.grid(column=3, row=0)

imageFrame = ttk.Frame(guiFrame, width=640, height=360)
imageFrame.grid(column=0, row=1)

img_1 = ttk.Label(imageFrame)
img_1.grid(row=0, column=0)

# Initialize webcam and MediaPipe modules
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

# Initialize MediaPipe solutions
hand_tracker = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
pose_tracker = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# FPS Calculation
fps_start_time = None  # Initialize to None to handle the first frame

def myloop():
    global fps_start_time  # Declare fps_start_time as global to modify it inside the loop

    ignore, frame = cam.read()
    if not ignore:
        return

    # Flip the frame horizontally for better user experience
    frame = cv2.flip(frame, 1)

    # Convert frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = frame

    # Hand tracking
    if b3.get():
        hands_results = hand_tracker.process(rgb_frame)
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(result, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Pose estimation
    if b2.get():
        pose_results = pose_tracker.process(rgb_frame)
        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(result, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Face detection
    if b1.get():
        face_results = face_detector.process(rgb_frame)
        if face_results.detections:
            for detection in face_results.detections:
                mp_drawing.draw_detection(result, detection)

    # Calculate FPS
    if fps_start_time is not None:  # Only calculate FPS after the first frame
        fps_end_time = cv2.getTickCount()
        fps_time = (fps_end_time - fps_start_time) / cv2.getTickFrequency()
        fps = int(1 / fps_time)
    else:
        fps = 0  # Initial FPS is 0 until the first frame

    fps_start_time = cv2.getTickCount()  # Update the start time for the next frame

    # Display FPS on the frame
    cv2.putText(result, f'{fps} FPS', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Convert frame for Tkinter
    frameRGBA = cv2.cvtColor(result, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(frameRGBA)
    imgtk = ImageTk.PhotoImage(image=img)

    img_1.imgtk = imgtk
    img_1.configure(image=imgtk)

    root.after(10, myloop)

# Start the loop
myloop()

root.mainloop()

# Release the camera and clean up
cam.release()