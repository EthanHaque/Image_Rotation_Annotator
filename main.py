import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from concurrent.futures import ThreadPoolExecutor


class ImageRotatorApp:
    def __init__(self, root):
        self.setup_ui(root)
        self.initialize_variables()

        self.executor = ThreadPoolExecutor(max_workers=1)  # Create a ThreadPoolExecutor

    def setup_ui(self, root):
        self.setup_menu(root)
        self.setup_controls(root)
        self.setup_bindings(root)

    def setup_menu(self, root):
        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="Open Directory",
            command=lambda: self.executor.submit(self.load_images),
        )
        menu_bar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menu_bar)

    def setup_controls(self, root):
        self.slider = tk.Scale(
            root, from_=0, to=0, orient=tk.HORIZONTAL, command=self.on_slider_changed
        )
        self.slider.pack()

        self.canvas = tk.Canvas(root, width=768, height=1024)
        self.canvas.pack()

    def setup_bindings(self, root):
        self.canvas.bind("<Button-1>", self.start_rotation)
        self.canvas.bind("<B1-Motion>", self.perform_rotation)
        self.canvas.bind("<ButtonRelease-1>", self.end_rotation)
        self.canvas.bind("<Double-Button-1>", self.reset_rotation)
        self.canvas.bind("<Button-2>", self.rotate_180_degrees)
        self.canvas.bind("<Button-3>", self.rotate_90_degrees)

        root.bind("<Configure>", self.on_canvas_resized)
        root.bind("f", self.next_image)
        root.bind("d", self.previous_image)

    def initialize_variables(self):
        self.images = []
        self.image_files = []
        self.current_image_index = 0
        self.group_size = 20
        self.original_image = None
        self.tk_image = None
        self.rotation_angle = 0
        self.start_x = self.start_y = None
        self.loading_thread = None

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = Image.open(file_path)
            self.rotation_angle = 0  # Reset the rotation angle
            self.on_canvas_resized(None)  # Resize the image to fit the canvas

    def load_images(self):
        directory_path = filedialog.askdirectory()
        self.images = [] 
        if directory_path:
            # Get a list of all files in the directory
            files = os.listdir(directory_path)
            files = sorted(files, key=lambda x: x.lower())

            # Filter the list to include only image files
            self.image_files = [
                os.path.join(directory_path, f)
                for f in files
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
            ]

            # Update the slider to reflect the number of images
            self.slider.config(to=len(self.image_files) - 1)
            self.slider.set(0)

            # Start a new thread to load the images in the background
            self.executor.submit(self.load_next_group)

    def on_slider_changed(self, value):
        # Change the current image when the slider value changes
        self.current_image_index = int(value)
        self.original_image = self.images[self.current_image_index]
        self.on_canvas_resized(None)

    def load_next_group(self):
        # Determine the start and end indices for the next group of images
        start_index = len(self.images)
        end_index = start_index + self.group_size

        # Load the next group of images
        for i in range(start_index, min(end_index, len(self.image_files))):
            try:
                with Image.open(self.image_files[i]) as img:
                    self.images.append(img.copy())
            except OSError:
                print(f"Failed to load image: {self.image_files[i]}")

        # Update the index at which the last group started
        self.last_group_start_index = start_index

        # Reset the rotation angle and load the first image of the new group
        if start_index == 0:
            self.rotation_angle = 0
            self.original_image = self.images[0]
            self.on_canvas_resized(None)

    def next_image(self, event=None):
        # Return immediately if no images are loaded
        if len(self.images) == 0:
            return

        # Move to the next image in the list
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
        self.original_image = self.images[self.current_image_index]
        self.on_canvas_resized(None)

        self.slider.set(self.current_image_index)

        # If we're more than halfway through the last loaded group, start loading the next group
        if (
            self.current_image_index
            > self.last_group_start_index + self.group_size // 2
        ):
            self.executor.submit(self.load_next_group)

    def previous_image(self, event=None):
        # Return immediately if no images are loaded
        if len(self.images) == 0:
            return

        # Move to the previous image in the list
        if self.current_image_index > 0:
            self.current_image_index -= 1
        self.original_image = self.images[self.current_image_index]
        self.on_canvas_resized(None)

        self.slider.set(self.current_image_index)

    def on_canvas_resized(self, event):
        if self.original_image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_aspect = self.original_image.width / self.original_image.height
            canvas_aspect = canvas_width / canvas_height

            if image_aspect > canvas_aspect:
                # If image is wider than canvas (relative to their heights), set width to canvas width and scale height
                width = min(canvas_width, self.original_image.width)
                height = int(width / image_aspect)
            else:
                # If image is taller than canvas (relative to their widths), set height to canvas height and scale width
                height = min(canvas_height, self.original_image.height)
                width = int(height * image_aspect)

            self.image = self.original_image.resize((width, height), Image.LANCZOS)
            self.update_canvas()

    def start_rotation(self, event):
        self.start_x, self.start_y = event.x, event.y

    def perform_rotation(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        rotation_sensitivity = 0.2
        self.rotation_angle -= (dx + dy) * rotation_sensitivity
        self.rotation_angle %= 360
        self.update_canvas()
        self.start_x, self.start_y = event.x, event.y

    def end_rotation(self, _):
        pass

    def rotate_90_degrees(self, _):
        self.rotation_angle += 90
        self.rotation_angle %= 360
        self.update_canvas()

    def rotate_180_degrees(self, _):
        self.rotation_angle += 180
        self.rotation_angle %= 360
        self.update_canvas()

    def reset_rotation(self, _):
        self.rotation_angle = 0
        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        rotated_image = self.image.rotate(self.rotation_angle, resample=Image.BILINEAR)
        self.tk_image = ImageTk.PhotoImage(rotated_image)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2, image=self.tk_image
        )
        self.draw_grid_on_canvas()

    def draw_grid_on_canvas(self):
        grid_size = 25
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = self.image.width
        image_height = self.image.height

        # Calculate the center of the canvas
        center_x = canvas_width // 2
        center_y = canvas_height // 2

        # Calculate the start and end points for the grid lines
        start_x = center_x - image_width // 2
        end_x = center_x + image_width // 2
        start_y = center_y - image_height // 2
        end_y = center_y + image_height // 2

        # Draw the vertical grid lines
        for i in range(start_x, end_x, grid_size):
            self.canvas.create_line(
                [(i, start_y), (i, end_y)], fill="white", stipple="gray25"
            )

        # Draw the horizontal grid lines
        for i in range(start_y, end_y, grid_size):
            self.canvas.create_line(
                [(start_x, i), (end_x, i)], fill="white", stipple="gray25"
            )


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = ImageRotatorApp(root)
    root.mainloop()
