import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor
import csv


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

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="Open Directory",
            command=lambda: self.executor.submit(self.open_directory),
        )
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Export menu
        export_menu = tk.Menu(menu_bar, tearoff=0)
        export_menu.add_command(
            label="Export Annotations",
            command=self.export_annotations_dialog,
        )
        menu_bar.add_cascade(label="Export", menu=export_menu)

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
        self.group_size = 30
        self.current_image = None
        self.rotation_angle = 0
        self.rotation_angles = []
        self.start_x = self.start_y = None
        self.loading_thread = None

    def export_annotations_dialog(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv")
        if filename:
            self.export_annotations(filename)

    def export_annotations(self, filename):
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Image", "Rotation Angle"])
            image_files_subset = self.image_files[: self.current_image_index + 1]
            rotation_angles_subset = self.rotation_angles[
                : self.current_image_index + 1
            ]
            for image_file, rotation_angle in zip(
                image_files_subset, rotation_angles_subset
            ):
                writer.writerow([image_file, rotation_angle])

    def open_directory(self):
        directory_path = filedialog.askdirectory()
        self.images = []
        if directory_path:
            # Get a list of all files in the directory
            # files = os.listdir(directory_path)
            # files = sorted(files, key=lambda x: x.lower())

            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                        self.image_files.append(os.path.join(root, file))

            self.image_files = sorted(self.image_files, key=lambda x: x.lower())

            # Filter the list to include only image files
            # self.image_files = [
            #     os.path.join(directory_path, f)
            #     for f in files
            #     if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
            # ]

            # Update the slider to reflect the number of images
            self.slider.config(to=len(self.image_files) - 1)
            self.slider.set(0)

            self.images = [None] * len(self.image_files)
            self.rotation_angles = [0] * len(self.image_files)

            # Start a new thread to load the images in the background
            self.executor.submit(self.load_images, range(self.group_size))

    def load_image_at_index(self, index):
        if index < 0 or index >= len(self.image_files):
            return None
        try:
            with Image.open(self.image_files[index]) as img:
                self.images[index] = img.copy()
        except OSError:
            print(f"Failed to load image: {self.image_files[index]}")

    def on_slider_changed(self, value):
        self.current_image_index = int(value)
        if self.images[self.current_image_index] is None:
            self.load_image_at_index(self.current_image_index)

        self.current_image = self.images[self.current_image_index]
        self.rotation_angle = self.rotation_angles[self.current_image_index]
        self.on_canvas_resized(None)

        # Preload nearby images and clear unused ones
        window = range(
            max(0, self.current_image_index - self.group_size // 2),
            min(len(self.image_files), self.current_image_index + self.group_size // 2),
        )
        self.executor.submit(self.load_images, window)
        self.clear_unused_images()

    def load_images(self, indices):
        # Load images at the given indices
        for i in indices:
            if i < 0 or i >= len(self.image_files):
                continue
            if self.images[i] is None:
                self.load_image_at_index(i)

        if self.current_image_index == 0:
            self.rotation_angle = self.rotation_angles[0]
            self.current_image = self.images[0]
            self.on_canvas_resized(None)

    def next_image(self, event=None):
        # Return immediately if no images are loaded
        if len(self.images) == 0:
            return

        # Move to the next image in the list
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
        self.current_image = self.images[self.current_image_index]
        self.on_canvas_resized(None)

        self.slider.set(self.current_image_index)

        # Load the next group of images if there are less than half a group left to load
        window = self.images[
            self.current_image_index + 1 : self.current_image_index + self.group_size
        ]
        if None in window[len(window) // 2 :]:
            none_indices = [i for i, x in enumerate(window) if x is None]
            none_indices = [i + self.current_image_index + 1 for i in none_indices]
            self.executor.submit(self.load_images, none_indices)

    def previous_image(self, event=None):
        # Return immediately if no images are loaded
        if len(self.images) == 0:
            return

        # Move to the previous image in the list
        if self.current_image_index > 0:
            self.current_image_index -= 1

        if self.images[self.current_image_index] is None:
            # If the image hasn't been loaded yet, load it
            # self.executor.submit(self.load_image_at_index, self.current_image_index)
            self.load_image_at_index(self.current_image_index)

        self.current_image = self.images[self.current_image_index]
        self.on_canvas_resized(None)

        self.slider.set(self.current_image_index)

        window = self.images[
            self.current_image_index - self.group_size : self.current_image_index - 1
        ]
        if None in window[: len(window) // 2]:
            none_indices = [i for i, x in enumerate(window) if x is None]
            none_indices = [
                i + self.current_image_index - self.group_size for i in none_indices
            ]
            none_indices.reverse()  # Load images closest to the current image first
            self.executor.submit(self.load_images, none_indices)

    def on_canvas_resized(self, event):
        if self.current_image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_aspect = self.current_image.width / self.current_image.height
            canvas_aspect = canvas_width / canvas_height

            if image_aspect > canvas_aspect:
                # If image is wider than canvas (relative to their heights), set width to canvas width and scale height
                width = min(canvas_width, self.current_image.width)
                height = int(width / image_aspect)
            else:
                # If image is taller than canvas (relative to their widths), set height to canvas height and scale width
                height = min(canvas_height, self.current_image.height)
                width = int(height * image_aspect)

            self.current_image = self.current_image.resize(
                (width, height), resample=Image.BILINEAR
            )
            self.update_canvas()

    def start_rotation(self, event):
        self.start_x, self.start_y = event.x, event.y

    def perform_rotation(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        rotation_sensitivity = 0.2
        self.rotation_angle -= (dx + dy) * rotation_sensitivity
        self.rotation_angle %= 360
        self.rotation_angles[self.current_image_index] = self.rotation_angle
        self.update_canvas()
        self.start_x, self.start_y = event.x, event.y

    def end_rotation(self, _):
        pass

    def rotate_90_degrees(self, _):
        self.rotation_angle += 90
        self.rotation_angle %= 360
        self.rotation_angles[self.current_image_index] = self.rotation_angle
        self.update_canvas()

    def rotate_180_degrees(self, _):
        self.rotation_angle += 180
        self.rotation_angle %= 360
        self.rotation_angles[self.current_image_index] = self.rotation_angle
        self.update_canvas()

    def reset_rotation(self, _):
        self.rotation_angle = 0
        self.rotation_angles[self.current_image_index] = 0
        self.update_canvas()

    def update_canvas(self):
        rotated_image = self.current_image.rotate(
            self.rotation_angle, resample=Image.BILINEAR
        )

        self.rotated_image = rotated_image.convert("RGB")
        self.tk_image = tk.PhotoImage(
            data=self.convert_image_to_png_data(rotated_image)
        )

        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2, image=self.tk_image
        )
        self.draw_grid_on_canvas()

    def convert_image_to_png_data(self, image):
        from io import BytesIO

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def clear_unused_images(self):
        min_index = max(0, self.current_image_index - self.group_size)
        max_index = min(
            len(self.image_files), self.current_image_index + self.group_size
        )
        for i in range(len(self.images)):
            if i < min_index or i > max_index:
                self.images[i] = None  # Clear from memory

    def draw_grid_on_canvas(self):
        grid_size = 25
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = self.current_image.width
        image_height = self.current_image.height

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
    root.geometry("1200x900")
    app = ImageRotatorApp(root)
    root.mainloop()
