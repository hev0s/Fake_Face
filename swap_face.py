import cv2
import numpy as np
import dlib
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import urllib.request
import uuid


class FaceSwapApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.load_models()

        self.source_image = None
        self.target_image = None
        self.result_image = None
        self.source_path = ""
        self.target_path = ""

        self.display_width = 400
        self.display_height = 300

    def setup_ui(self):
        self.root.title("Professional Face Swap v2.3")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.image_frame = Frame(main_frame)
        self.image_frame.pack(fill=BOTH, expand=True)

        self.source_frame = LabelFrame(self.image_frame, text="Source Image")
        self.source_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.source_label = Label(self.source_frame)
        self.source_label.pack()

        self.target_frame = LabelFrame(self.image_frame, text="Target Image")
        self.target_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.target_label = Label(self.target_frame)
        self.target_label.pack()

        self.result_frame = LabelFrame(self.image_frame, text="Result Image")
        self.result_label = Label(self.result_frame)
        self.result_label.pack()

        control_frame = Frame(main_frame)
        control_frame.pack(fill=X, pady=10)

        Button(control_frame, text="Load Source", command=self.load_source).grid(row=0, column=0, padx=5)
        Button(control_frame, text="Load Target", command=self.load_target).grid(row=0, column=1, padx=5)
        Button(control_frame, text="Swap Faces", command=self.swap_faces).grid(row=0, column=2, padx=5)

        self.save_button = Button(control_frame, text="Save Result", command=self.save_result, state=DISABLED)
        self.save_button.grid(row=0, column=3, padx=5)

        Button(control_frame, text="Generate AI Face", command=self.generate_ai_face).grid(row=0, column=4, padx=5)
        Button(control_frame, text="Webcam Source", command=lambda: self.capture_from_webcam(is_source=True)).grid(
            row=0, column=5, padx=5)
        Button(control_frame, text="Webcam Target", command=lambda: self.capture_from_webcam(is_source=False)).grid(
            row=0, column=6, padx=5)
        Button(control_frame, text="Live Swap Video", command=self.open_live_video).grid(row=0, column=7, padx=5)

        settings_frame = Frame(control_frame)
        settings_frame.grid(row=1, column=0, columnspan=8, pady=5)

        Label(settings_frame, text="Blend Amount:").grid(row=0, column=0)
        self.blend_scale = Scale(settings_frame, from_=0, to=100, orient=HORIZONTAL, length=150)
        self.blend_scale.set(65)
        self.blend_scale.grid(row=0, column=1)
        self.blend_scale.bind("<ButtonRelease-1>", self.update_blend)

        Label(settings_frame, text="Color Adjustment:").grid(row=0, column=2)
        self.color_scale = Scale(settings_frame, from_=0, to=100, orient=HORIZONTAL, length=150)
        self.color_scale.set(50)
        self.color_scale.grid(row=0, column=3)
        self.color_scale.bind("<ButtonRelease-1>", self.update_color)

        self.status_var = StringVar()
        self.status_var.set("Ready to load images")
        status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W)
        status_bar.pack(side=BOTTOM, fill=X)

        for i in range(3):
            self.image_frame.columnconfigure(i, weight=1)
        self.image_frame.rowconfigure(0, weight=1)

    def load_models(self):
        try:
            self.detector = dlib.get_frontal_face_detector()
            model_path = "shape_predictor_68_face_landmarks.dat"
            if not os.path.exists(model_path):
                raise FileNotFoundError("Dlib model file not found.")
            self.predictor = dlib.shape_predictor(model_path)
        except Exception as e:
            messagebox.showerror("Model Load Error", str(e))
            self.root.destroy()

    def load_image(self, is_source=True):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not path:
            return
        try:
            image = cv2.imread(path)
            if image is None:
                raise ValueError("Invalid image file")
            if is_source:
                self.source_image = image
                self.source_path = path
                self.show_image(image, self.source_label)
                self.status_var.set(f"Source image loaded: {os.path.basename(path)}")
            else:
                self.target_image = image
                self.target_path = path
                self.show_image(image, self.target_label)
                self.status_var.set(f"Target image loaded: {os.path.basename(path)}")
            if self.source_image is not None and self.target_image is not None:
                self.status_var.set("Ready to perform face swap")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            # sprint 1 finished
            # sprint 2 start

    def load_source(self):
        self.load_image(is_source=True)

    def load_target(self):
        self.load_image(is_source=False)

    def capture_from_webcam(self, is_source=True):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot open webcam.")
            return

        self.status_var.set("SPACE: Capture image | ESC: Exit")
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
        captured = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Webcam", frame)
            key = cv2.waitKey(1)
            if key == 32:  # SPACE
                captured = frame.copy()
                break
            elif key == 27:  # ESC
                break

        cap.release()
        cv2.destroyAllWindows()

        if captured is not None:
            if is_source:
                self.source_image = captured
                self.source_path = "webcam_source.jpg"
                self.show_image(captured, self.source_label)
                self.status_var.set("Source image captured from webcam.")
            else:
                self.target_image = captured
                self.target_path = "webcam_target.jpg"
                self.show_image(captured, self.target_label)
                self.status_var.set("Target image captured from webcam.")
            if self.source_image is not None and self.target_image is not None:
                self.status_var.set("Ready to perform face swap.")
