class ImageViewer {
  constructor(inputElementId, galleryElementId) {
    this.inputElement = document.getElementById(inputElementId);
    this.galleryElement = document.getElementById(galleryElementId);
    this.initialize();
  }

  initialize() {
    this.inputElement.addEventListener("change", (event) =>
      this.handleFileSelection(event)
    );
  }

  handleFileSelection(event) {
    const files = event.target.files;
    this.galleryElement.innerHTML = "";
    Array.from(files).forEach((file) => {
      if (file.type.startsWith("image/")) {
        this.displayImage(file);
      }
    });
  }

  displayImage(file) {
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.onload = function () {
      URL.revokeObjectURL(this.src);
    };
    this.galleryElement.appendChild(img);
  }
}

new ImageViewer("directoryInput", "imageGallery");
