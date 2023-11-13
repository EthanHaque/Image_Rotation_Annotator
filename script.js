class ImageViewer {
  constructor(
    inputElementId,
    galleryElementId,
    selectedImageId,
    rotationSliderId
  ) {
    this.inputElement = document.getElementById(inputElementId);
    this.galleryElement = document.getElementById(galleryElementId);
    this.selectedImage = document.getElementById(selectedImageId);
    this.rotationSlider = document.getElementById(rotationSliderId);
    this.initialize();
  }

  initialize() {
    this.inputElement.addEventListener("change", (event) =>
      this.handleFileSelection(event)
    );
    this.rotationSlider.addEventListener("input", (event) =>
      this.rotateImage(event)
    );
  }

  handleFileSelection(event) {
    const files = event.target.files;
    this.galleryElement.innerHTML = "";
    Array.from(files).forEach((file) => {
      if (file.type.startsWith("image/")) {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.onclick = () => this.selectImage(file);
        this.galleryElement.appendChild(img);
      }
    });
  }

  selectImage(file) {
    this.selectedImage.src = URL.createObjectURL(file);
    this.selectedImage.onload = function () {
      URL.revokeObjectURL(this.src);
    };
    this.rotationSlider.value = 0; // Reset rotation slider
  }

  rotateImage(event) {
    const angle = event.target.value;
    this.selectedImage.style.transform = `rotate(${angle}deg)`;
  }
}

new ImageViewer(
  "directoryInput",
  "imageGallery",
  "selectedImage",
  "rotationSlider"
);
