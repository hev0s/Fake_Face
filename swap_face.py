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