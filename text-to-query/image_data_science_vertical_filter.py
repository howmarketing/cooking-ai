# Ensure you have the required libraries installed. You can use the following command in a terminal or Jupyter cell:
# pip install numpy matplotlib opencv-python-headless pillow

import numpy as np
import matplotlib.pyplot as plt
import cv2
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image


# Function to apply horizontal filtering
def horizontal_filtering(image):
    """
    Apply horizontal filtering to an image to emphasize horizontal edges.

    Parameters:
    image (numpy.ndarray): Input image in BGR format.

    Returns:
    numpy.ndarray: Filtered image emphasizing horizontal edges.
    """
    # Convert image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    display_image(gray_image, "Gray Image")
    # Create an empty array to store the filtered image
    filtered_image = np.zeros_like(gray_image)

    # Get the image dimensions
    height, width = gray_image.shape

    # Apply horizontal filtering
    for i in range(1, height):
        for j in range(width):
            # Compute the difference between the pixel and the pixel above it
            filtered_image[i, j] = abs(
                int(gray_image[i, j]) - int(gray_image[i - 1, j])
            )

    return filtered_image


# Load a PNG image
def load_image(image_path):
    """
    Load an image from the specified file path.

    Parameters:
    image_path (str): Path to the image file.

    Returns:
    numpy.ndarray: Loaded image in BGR format.
    """
    return cv2.imread(image_path)


# Display the image
def display_image(image, title="Image"):
    """
    Display an image using matplotlib.

    Parameters:
    image (numpy.ndarray): Image to be displayed.
    title (str): Title of the displayed image.
    """
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()


# Main function to run the code
def main():
    """
    Load an image, apply horizontal filtering, and display the original and filtered images.
    """
    # Create a Tk root window (it will not be shown)
    root = Tk()
    root.withdraw()  # Hide the root window

    # Open a file dialog and ask for the image file
    image_path = askopenfilename(
        title="Select an Image File",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
    )

    if image_path:  # Check if a file was selected
        # Load the image
        image = load_image(image_path)

        # Apply horizontal filtering
        filtered_image = horizontal_filtering(image)

        # Display the original and filtered images
        display_image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), title="Original Image")
        print("\n" * 2, "=" * 80, "\n" * 2)
        display_image(filtered_image, title="Filtered Image")
    else:
        print("No file selected.")


# Run the main function
if __name__ == "__main__":
    main()
