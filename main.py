import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import os

class ImageViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Image Viewer')
        self.geometry('800x600')

        self.images = []
        self.current_image = None
        self.current_index = -1
        self.rotation_angle = 0

        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self, text='Load Images', command=self.load_images)
        self.load_button.pack()

        self.canvas = tk.Canvas(self, width=600, height=400)
        self.canvas.pack()

        self.rotate_slider = tk.Scale(self, from_=0, to=360, orient='horizontal', command=self.rotate_image)
        self.rotate_slider.pack()

        self.prev_button = tk.Button(self, text='Previous', command=lambda: self.navigate(-1))
        self.prev_button.pack(side='left')

        self.next_button = tk.Button(self, text='Next', command=lambda: self.navigate(1))
        self.next_button.pack(side='right')

    def load_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.bmp')])
        self.images = [Image.open(path) for path in file_paths]
        if self.images:
            self.current_index = 0
            self.show_image()

    def show_image(self):
        if self.current_index >= 0 and self.current_index < len(self.images):
            self.current_image = ImageTk.PhotoImage(self.images[self.current_index])
            self.canvas.create_image(300, 200, image=self.current_image)

    def navigate(self, direction):
        self.current_index = (self.current_index + direction) % len(self.images)
        self.rotation_angle = 0
        self.rotate_slider.set(0)
        self.show_image()

    def rotate_image(self, angle):
        if self.current_index >= 0 and self.current_index < len(self.images):
            angle = int(angle) - self.rotation_angle
            self.rotation_angle += angle
            rotated_image = ImageOps.exif_transpose(self.images[self.current_index].rotate(angle, expand=True))
            self.images[self.current_index] = rotated_image
            self.current_image = ImageTk.PhotoImage(rotated_image)
            self.canvas.create_image(300, 200, image=self.current_image)

if __name__ == '__main__':
    app = ImageViewer()
    app.mainloop()
