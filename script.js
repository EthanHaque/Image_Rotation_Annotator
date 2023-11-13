class ImageViewer {
  constructor(
    inputElementId,
    selectedImageId,
    rotationSliderId,
    prevButtonId,
    nextButtonId
  ) {
    this.inputElement = document.getElementById(inputElementId);
    this.selectedImage = document.getElementById(selectedImageId);
    this.rotationSlider = document.getElementById(rotationSliderId);
    this.prevButton = document.getElementById(prevButtonId);
    this.nextButton = document.getElementById(nextButtonId);
    this.images = [];
    this.imageRotations = {};
    this.currentIndex = 0;
    this.initialize();
  }

  initialize() {
    this.inputElement.addEventListener("change", (event) =>
      this.handleFileSelection(event)
    );
    this.rotationSlider.addEventListener("input", (event) =>
      this.rotateImage(event)
    );
    this.prevButton.addEventListener("click", () => this.navigateImage(-1));
    this.nextButton.addEventListener("click", () => this.navigateImage(1));
  }

  handleFileSelection(event) {
    const files = event.target.files;
    this.images = Array.from(files).filter((file) =>
      file.type.startsWith("image/")
    );
    this.images.forEach((file, index) => {
      this.imageRotations[index] = 0; // Initialize rotation state for each image
    });
    this.currentIndex = 0;
    this.displayImage();
  }

  displayImage() {
    if (this.images.length > 0) {
      const file = this.images[this.currentIndex];
      const currentRotation = this.imageRotations[this.currentIndex];
      this.selectedImage.src = URL.createObjectURL(file);
      this.selectedImage.onload = () => {
        URL.revokeObjectURL(this.src);
        this.selectedImage.style.transform = `rotate(${currentRotation}deg)`;
      };
      this.rotationSlider.value = currentRotation;
    }
  }

  rotateImage(event) {
    const angle = event.target.value;
    this.selectedImage.style.transform = `rotate(${angle}deg)`;
    this.imageRotations[this.currentIndex] = angle;
  }

  navigateImage(direction) {
    this.saveCurrentImageRotation();
    this.currentIndex =
      (this.currentIndex + direction + this.images.length) % this.images.length;
    this.displayImage();
  }

  saveCurrentImageRotation() {
    const currentRotation = parseInt(this.rotationSlider.value, 10);
    this.imageRotations[this.currentIndex] = currentRotation;
  }
}

new ImageViewer(
  "directoryInput",
  "selectedImage",
  "rotationSlider",
  "prevButton",
  "nextButton"
);
