import tkinter as tk
from tkinter import ttk
from tkinter import *
# from tkinter import messagebox
# import time
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
# import threading
import os

from pyparsing import col


class CameraFeed(ttk.Frame):
    def __init__(self, parent,camera_index=0):
        super().__init__(parent)
        self.camera_index = camera_index


        # Initialize MediaPipe modules
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils

        # Initialize detection modules
        self.hand_tracker = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.pose_tracker = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.face_detector = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)

        # Create controls
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(fill='x')

        self.face_detection = tk.BooleanVar()
        self.body_pose = tk.BooleanVar()
        self.hand_tracking = tk.BooleanVar()

        ttk.Checkbutton(self.control_frame, text='Face Detection', variable=self.face_detection).pack(side='left')
        ttk.Checkbutton(self.control_frame, text='Body Pose', variable=self.body_pose).pack(side='left')
        ttk.Checkbutton(self.control_frame, text='Hands', variable=self.hand_tracking).pack(side='left')



        # Create camera feed label
        self.feed_label = ttk.Label(self)
        self.feed_label.pack(expand=True, fill='both')

        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 50)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 50)

        self.fps_start_time = None
        self.update_feed()


    def update_feed(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = frame

            # Process detections based on checkboxes
            if self.hand_tracking.get():
                hands_results = self.hand_tracker.process(rgb_frame)
                if hands_results.multi_hand_landmarks:
                    for hand_landmarks in hands_results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(result, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            if self.body_pose.get():
                pose_results = self.pose_tracker.process(rgb_frame)
                if pose_results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(result, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            if self.face_detection.get():
                face_results = self.face_detector.process(rgb_frame)
                if face_results.detections:
                    for detection in face_results.detections:
                        self.mp_drawing.draw_detection(result, detection)

            # Calculate and display FPS
            if self.fps_start_time is not None:
                fps_end_time = cv2.getTickCount()
                fps_time = (fps_end_time - self.fps_start_time) / cv2.getTickFrequency()
                fps = int(1 / fps_time)
                cv2.putText(result, f'{fps} FPS', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            self.fps_start_time = cv2.getTickCount()

            # Convert frame for display
            frame_rgba = cv2.cvtColor(result, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(frame_rgba)
            img_tk = ImageTk.PhotoImage(image=img)
            self.feed_label.imgtk = img_tk
            self.feed_label.configure(image=img_tk)

            self.after(10, self.update_feed)

    def cleanup(self):
        if self.camera.isOpened():
            self.camera.release()






class CCTVGridFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.camera_feeds = {}  # Store camera feeds and their zoom states
        self.zoom_level = {}  # To keep track of each camera's zoom level


        # Initialize variables
        self.current_page = 0
        self.cameras_per_page = 16
        self.total_cameras = 32
        self.total_pages = self.total_cameras // self.cameras_per_page
        self.zoom_scale = 1.0

        self.camera_labels = []
        self.camera_recording = {}  # Track recording status for each camera
        self.video_writers = {}  # Store VideoWriter objects for recording



        # Configure grid weights
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

        # Create camera frames
        self.camera_frames = []
        for row in range(4):
            for col in range(4):
                frame = ttk.Frame(self, relief="solid", borderwidth=3, width=180,height=130)
                frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

                frame.pack_propagate(False)



                overlay_frame = ttk.Frame(frame)
                overlay_frame.pack(expand=True, fill='both')

                # First camera position gets the live feed
                if row == 0 and col == 0:
                    camera_feed = CameraFeed(frame, camera_index=0)
                    camera_feed.pack(expand=True, fill='both')
                elif row == 0 and col == 1:
                    camera_feed = CameraFeed(frame, camera_index=1)  # Second camera
                    camera_feed.pack(expand=True, fill='both')
                else:
                    # Create label for other camera feeds
                    label = ttk.Label(
                        frame,
                        text=f"Camera {row * 4 + col + 1}",
                        background='black',
                        foreground='white'
                    )
                    label.pack(expand=True, fill='both', padx=35, pady=35)


        start_btn = ttk.Button(
            overlay_frame,
            text="Start Rec",
            command=lambda pos=len(self.camera_labels) - 1: self.start_recording(pos)
        )
        start_btn.place(relx=0.1, rely=0.8, anchor="sw")

        stop_btn = ttk.Button(
            overlay_frame,
            text="Stop Rec",
            command=lambda pos=len(self.camera_labels) - 1: self.stop_recording(pos)
        )
        stop_btn.place(relx=0.9, rely=0.8, anchor="se")

        # noinspection PyTypeChecker
        self.camera_frames.append({
            'frame': frame,
            'label': Label if row != 0 or col != 0 else None,
            'start_btn': start_btn,
            'stop_btn': stop_btn
         })

        self.setup_navigation()

    def setup_navigation(self):
        """Setup pagination navigation controls"""
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.grid(row=4, column=0, columnspan=4, pady=10)


        self.prev_button = ttk.Button(
            self.nav_frame,
            text="Previous Page",
            command=self.previous_page
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.page_label = ttk.Label(
            self.nav_frame,
            text=f"Page {self.current_page + 1}/{self.total_pages}"
        )
        self.page_label.pack(side=tk.LEFT, padx=20)

        self.next_button = ttk.Button(
            self.nav_frame,
            text="Next Page",
            command=self.next_page
        )
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.update_button_states()



    def next_page(self):
        if self.current_page < (self.total_pages - 1):
            self.current_page += 1
            self.update_camera_display()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_camera_display()

    def update_camera_display(self):
        start_camera = self.current_page * self.cameras_per_page

        # Update camera labels except for the first camera
        for i, camera_frame in enumerate(self.camera_frames[1:], 1):
            camera_number = start_camera + i + 1
            if camera_frame['label']:
                camera_frame['label'].configure(text=f"Camera {camera_number}")

                # Show/hide cameras based on current page
                if camera_number <= self.total_cameras:
                    camera_frame['frame'].grid()
                else:
                    camera_frame['frame'].grid_remove()

                # Update navigation elements
                self.page_label.configure(text=f"Page {self.current_page + 1}/{self.total_pages}")
                self.update_button_states()

    def update_button_states(self):
        """Update the state of navigation buttons"""
        if self.current_page > 0:
            self.prev_button.state(['!disabled'])
        else:
            self.prev_button.state(['disabled'])

        if self.current_page < (self.total_pages - 1):
            self.next_button.state(['!disabled'])
        else:
            self.next_button.state(['disabled'])

        self.prev_button.state(['!disabled'] if self.current_page > 0 else ['disabled'])
        self.next_button.state(['!disabled'] if self.current_page < (self.total_pages - 1) else ['disabled'])

    def start_recording(self, camera_position):
        if camera_position not in self.video_writers:
         os.makedirs("recordings", exist_ok=True)
        filename = f"recordings/camera_{camera_position + 1}.avi"
        fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
        self.video_writers[camera_position] = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
        self.camera_recording[camera_position] = True

    def stop_recording(self, camera_position):
        if camera_position in self.video_writers:
         self.camera_recording[camera_position] = False
        self.video_writers[camera_position].release()
        del self.video_writers[camera_position]


# def update_camera_display(self):
#         start_camera = self.current_page * self.cameras_per_page
#
#         for i, camera_frame in enumerate(self.camera_frames[1:], 1):  # Skip first camera
#             camera_number = start_camera + i + 1
#             if camera_frame['label']:
#                 camera_frame['label'].configure(text=f"Camera {camera_number}")
#
#         self.page_label.configure(text=f"Page {self.current_page + 1}/{self.total_pages}")
#         self.prev_button.state(['!disabled'] if self.current_page > 0 else ['disabled'])
#         self.next_button.state(['!disabled'] if self.current_page < (self.total_pages - 1) else ['disabled'])

def cleanup(self):
        # Cleanup camera resources
        for frame in self.camera_frames:
            if hasattr(frame.get('frame'), 'cleanup'):
              frame['frame'].cleanup()

def main():
    root = tk.Tk()
    root.title('CCTV Control Panel')
    root.geometry("11700x800")

    # Create menu
    menu = tk.Menu(root)
    live_menu = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label='live view', menu=live_menu)
    play_menu = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label='playback', menu=play_menu)
    l_menu = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label='log', menu=l_menu)
    con_menu = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label='configuration', menu=con_menu)

    # Create left frame (frame)
    frame = ttk.Frame(root, width=150, height=380, borderwidth=2, relief=tk.GROOVE)
    frame.pack_propagate(False)
    notebook = ttk.Notebook(frame)
    tab1 = ttk.Frame(notebook)

    # Add camera labels to tab1
    for i in range(1, 17):
        label = ttk.Label(tab1, text=f'camera {i:02d}')
        label.pack()

    notebook.add(tab1, text='Embedded net DVR')
    notebook.pack()
    frame.place(x=5, y=10)



    frame2 = ttk.Frame(root, width=455, height=50, borderwidth=2, relief=tk.GROOVE)
    frame2.pack_propagate(False)

    def zoom_in(self):
        self.zoom_scale += 0.1  # Increase zoom scale
        self.setup_camera_feed(1)  # Refresh the feed with zoomed image

    def zoom_out(self):
        self.zoom_scale = max(0.1, self.zoom_scale - 0.1)  # Decrease zoom scale, minimum 0.1
        self.setup_camera_feed(1)


    image_original = Image.open('cam.ico').resize((20, 20))
    image_tk = ImageTk.PhotoImage(image_original)

    fil_image = Image.open('rac2.ico').resize((20, 20))
    file_image_tk = ImageTk.PhotoImage(fil_image)

    zooi_image = Image.open('zoom_in.ico').resize((20, 20))
    zoom_in_image_tk = ImageTk.PhotoImage(zooi_image)


    zoo_image = Image.open('zom.ico').resize((20, 20))
    zoom_image_tk = ImageTk.PhotoImage(zoo_image)

    arr_image = Image.open('larr.ico').resize((20, 20))
    arrow_image_tk = ImageTk.PhotoImage(arr_image)

    arro_image = Image.open('narr.ico').resize((20, 20))
    next_image_tk = ImageTk.PhotoImage(arro_image)

    mic_image = Image.open('mic.ico').resize((20, 20))
    Mice_image_tk = ImageTk.PhotoImage(mic_image)

    mut_image = Image.open('mute.ico').resize((20, 20))
    mute_image_tk = ImageTk.PhotoImage(mut_image)
    resiz_image = Image.open('resize.ico').resize((20, 20))
    resize_image_tk = ImageTk.PhotoImage(resiz_image)

    button = ttk.Button(frame2, image=image_tk)
    button.place(x=200, y=0)
    button1 = ttk.Button(frame2, image=file_image_tk)
    button1.place(x=170, y=0)
    zoom_in_button = ttk.Button(frame2, image=zoom_in_image_tk,  command= zoom_in)
    zoom_in_button.place(x=230, y=0)
    zoom_out_button = ttk.Button(frame2, image=zoom_image_tk,   command= zoom_out)
    zoom_out_button.place(x=260, y=0)
    button4 = ttk.Button(frame2, image=arrow_image_tk)
    button4.place(x=290, y=0)
    button5 = ttk.Button(frame2, image=next_image_tk)
    button5.place(x=320, y=0)
    button6 = ttk.Button(frame2, image=Mice_image_tk)
    button6.place(x=350, y=0)
    button7 = ttk.Button(frame2, image=mute_image_tk)
    button7.place(x=380, y=0)
    button8 = ttk.Button(frame2, image=resize_image_tk)
    button8.place(x=410, y=0)

    frame2.place(x=160, y=555)

    frame3 = ttk.Frame(root, width=200, height=350, borderwidth=2, relief=tk.GROOVE)
    frame3.pack_propagate(False)

    # Add PTZ label
    label9 = ttk.Label(frame3, text='PTZ', background='white')
    label9.place(x=0, y=0)
    arr_image = Image.open('lefcorn.png').resize((10, 10))
    arrow1_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('arrup.png').resize((10, 10))
    arrow2_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('arrrigh.png').resize((10, 10))
    arrow3_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('leftarrow.png').resize((10, 10))
    arrow4_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('circleup.png').resize((10, 10))
    arrow5_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('arrowright.png').resize((10, 10))
    arrow6_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('leftcorner.png').resize((10, 10))
    arrow7_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('downarrow.png').resize((10, 10))
    arrow8_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('rightcorner.png').resize((10, 10))
    arrow9_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('plus.png').resize((10, 10))
    arrow10_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('plus.png').resize((10, 10))
    arrow11_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('plus.png').resize((10, 10))
    arrow12_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('search.png').resize((10, 10))
    arrow13_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('music.png').resize((10, 10))
    arrow14_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('star.png').resize((10, 10))
    arrow15_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('minus.png').resize((10, 10))
    arrow16_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('minus.png').resize((10, 10))
    arrow17_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('minus.png').resize((10, 10))
    arrow18_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('flag.png').resize((40, 10))
    arrow19_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('bulb1.ico').resize((50, 10))
    arrow20_image_tk = ImageTk.PhotoImage(arr_image)
    arr_image = Image.open('sink.png').resize((50, 10))
    arrow21_image_tk = ImageTk.PhotoImage(arr_image)

    button1 = ttk.Button(frame3, image=arrow1_image_tk)
    button1.place(x=0, y=20)
    button2 = ttk.Button(frame3, image=arrow2_image_tk)
    button2.place(x=20, y=20)
    button3 = ttk.Button(frame3, image=arrow3_image_tk)
    button3.place(x=40, y=20)
    button4 = ttk.Button(frame3, image=arrow4_image_tk)
    button4.place(x=0, y=40)
    button5 = ttk.Button(frame3, image=arrow5_image_tk)
    button5.place(x=20, y=40)
    button6 = ttk.Button(frame3, image=arrow6_image_tk)
    button6.place(x=40, y=40)
    button7 = ttk.Button(frame3, image=arrow7_image_tk)
    button7.place(x=0, y=60)
    button8 = ttk.Button(frame3, image=arrow8_image_tk)
    button8.place(x=20, y=60)
    button9 = ttk.Button(frame3, image=arrow9_image_tk)
    button9.place(x=40, y=60)
    button10 = ttk.Button(frame3, image=arrow10_image_tk)
    button10.place(x=60, y=20)
    button11 = ttk.Button(frame3, image=arrow11_image_tk)
    button11.place(x=60, y=40)
    button12 = ttk.Button(frame3, image=arrow12_image_tk)
    button12.place(x=60, y=60)
    button13 = ttk.Button(frame3, image=arrow13_image_tk)
    button13.place(x=80, y=20)
    button14 = ttk.Button(frame3, image=arrow14_image_tk)
    button14.place(x=80, y=40)
    button15 = ttk.Button(frame3, image=arrow15_image_tk)
    button15.place(x=80, y=60)
    button16 = ttk.Button(frame3, image=arrow16_image_tk)
    button16.place(x=100, y=20)
    button17 = ttk.Button(frame3, image=arrow17_image_tk)
    button17.place(x=100, y=40)
    button18 = ttk.Button(frame3, image=arrow18_image_tk)
    button18.place(x=100, y=60)
    button20 = ttk.Button(frame3, image=arrow20_image_tk)
    button20.place(x=0, y=80)
    button21 = ttk.Button(frame3, image=arrow21_image_tk)
    button21.place(x=60, y=80)

    # Add scrollbar and list
    sb = ttk.Scrollbar(frame3)
    sb.pack(side='right', fill='y', ipadx=15)

    mylist = tk.Listbox(frame3, yscrollcommand=sb.set)
    for i in range(16):
        mylist.insert('end', f"preset {i}")
    mylist.pack(side='left', pady=100, fill='both', ipadx=20)
    sb.config(command=mylist.yview)

    frame3.place(x=910, y=10)

    frame4 = ttk.Frame(root, width=150, height=40, borderwidth=10, relief=tk.GROOVE)
    frame4.pack_propagate(False)

    items = ('HD', 'Mp4')
    video_string = tk.StringVar(value='Video parameters')
    combo = ttk.Combobox(frame4, textvariable=video_string)
    combo['value'] = items
    combo.pack()

    frame4.place(x=910, y=370)

    grid_frame = CCTVGridFrame(root,  height=170, width=400, relief=tk.GROOVE)
    grid_frame.place(x=160, y=5)

    def on_closing():
        grid_frame.cleanup()

        root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)


    root.configure(menu=menu)
    root.mainloop()


if __name__ == "__main__":
  main()