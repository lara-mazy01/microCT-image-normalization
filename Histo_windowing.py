import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib
  # Ensure GUI backend is used
import matplotlib.pyplot as plt
from skimage import io, img_as_ubyte
from PIL import Image  # For saving images as .bmp

# Initialize the tkinter window (hidden)
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)  # Ensure the file dialog opens in front

def rescaling_image():
    folder_dir = os.path.dirname(file_path)  # Get the directory of the selected file
    bmp_folder = os.path.join(folder_dir, 'bmp')

    # Create the folder if it doesn't exist
    if not os.path.exists(bmp_folder):
        os.makedirs(bmp_folder)
        print(f"Created folder: {bmp_folder}")

    # Step 3: Conversion process
    for filename in os.listdir(folder_dir):
        if filename.endswith(".tif") or filename.endswith(".tiff"):
            tiff_image_path = os.path.join(folder_dir, filename)
            image = io.imread(tiff_image_path)

            # Rescale the image based on the selected min/max values
            rescaled_image = np.clip(image, min_value, max_value)  # Clip values outside the range
            rescaled_image = (rescaled_image - min_value) / (max_value - min_value)  # Normalize to 0-1
            rescaled_image = img_as_ubyte(rescaled_image)  # Convert to 8-bit (0-255)

            # Save the rescaled image as BMP in the new folder
            bmp_image_path = os.path.join(bmp_folder, f"{os.path.splitext(filename)[0]}.bmp")
            Image.fromarray(rescaled_image).save(bmp_image_path, format="BMP")

    # Show completion message after conversion
    messagebox.showinfo("Conversion Completed", "All images have been successfully converted to BMP format!")
    
    # Step 4: Prepare to Save Before and After Images with Histograms
    # Create a new window to display results
    # display_window = tk.Toplevel(root)
    # display_window.title("Reference Image Before and After Conversion")

    # Original Image
    original_rescaled_image = np.clip(reference_image, min_value, max_value)  # Clip values
    original_rescaled_image = (original_rescaled_image - min_value) / (max_value - min_value)  # Normalize
    original_rescaled_image = img_as_ubyte(original_rescaled_image)  # Convert to 8-bit

    # Create a figure with subplots for the original and rescaled images and their histograms
    fig, ax = plt.subplots(2, 2, figsize=(12, 12))

    # Original Image
    ax[0, 0].imshow(reference_image, cmap='gray')
    ax[0, 0].set_title("Original Image")
    ax[0, 0].axis('off')  # Hide axis

    # Original Histogram
    ax[0, 1].plot(bins[:-1], hist)
    ax[0, 1].set_title("Original Histogram")
    ax[0, 1].set_xlabel("Pixel Intensity")
    ax[0, 1].set_ylabel("Frequency")

    # Rescaled Image
    ax[1, 0].imshow(original_rescaled_image, cmap='gray')
    ax[1, 0].set_title("Rescaled Image")
    ax[1, 0].axis('off')  # Hide axis

    # Rescaled Histogram
    rescaled_hist, rescaled_bins = np.histogram(original_rescaled_image, bins=256, range=(0, 255))
    ax[1, 1].plot(rescaled_bins[:-1], rescaled_hist)
    ax[1, 1].set_title("Rescaled Histogram")
    ax[1, 1].set_xlabel("Pixel Intensity")
    ax[1, 1].set_ylabel("Frequency")

    # Adjust layout
    plt.tight_layout()

    # Save the figure as a JPEG file
    #output_image_path = os.path.join(bmp_folder, 'histogram_results.jpg')
    #plt.savefig(output_image_path, format='jpeg')
    #plt.close(fig)  # Close the figure

    # Notify user that the image has been saved
    messagebox.showinfo("","Results Saved")
    plt.close()
    #messagebox.showinfo("Results Saved", f"Histogram results saved as: {output_image_path}")
    root.destroy()


# Open file selection dialog to choose reference image directly
file_path = filedialog.askopenfilename(
    title="Select Reference Image",
    filetypes=[("TIFF files", "*.tiff *.tif *.TIFF *.TIF")]  # Allow different TIFF extensions
)

# Reset the "topmost" attribute after the file dialog is opened
root.attributes("-topmost", False)

if file_path:
    print(f"Selected reference image: {file_path}")

    # Load the reference image
    reference_image = io.imread(file_path)
    if reference_image.dtype != np.uint16:
        print("Warning: The image is not 16-bit!")
    matplotlib.use('TkAgg')
    # Compute histogram
    flattened_image = reference_image.flatten()  # Flatten to 1D for histogram
    hist, bins = np.histogram(flattened_image, bins=65536, range=(0, 65535))  # 16-bit range

    # Plot the histogram for user to select min/max points
    plt.figure()
    plt.plot(bins[:-1], hist)
    plt.title("Select Min and Max Points for Histogram Normalization")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.grid()

    # Let the user select 2 points on the graph
    selected_points = plt.ginput(2)  # Select two points on the histogram
    plt.close()  # Close the histogram plot after selection

    # Extract the selected min and max points
    min_value, max_value = int(selected_points[0][0]), int(selected_points[1][0])
    print(f"Selected range: Min = {min_value}, Max = {max_value}")
    
    preview_rescaled_image = np.clip(reference_image, min_value, max_value)  # Clip values outside the range
    preview_rescaled_image = (preview_rescaled_image - min_value) / (max_value - min_value)  # Normalize to 0-1
    preview_rescaled_image = img_as_ubyte(preview_rescaled_image)  # Convert to 8-bit (0-255)
    
    preview_flattened_image = preview_rescaled_image.flatten()  # Flatten to 1D for histogram
    preview_hist, preview_bins = np.histogram(preview_flattened_image, bins=256, range=(0, 255))
    
    plt.figure()
    plt.plot(preview_bins[:-1], preview_hist)
    plt.title("Select Min and Max Points for Histogram Normalization")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.grid()

    # Step 1: Display confirmation message box
    confirm = messagebox.askyesnocancel("Reference Points Selected", "Convert to BMP [YES] or reselect points [NO]?")
    plt.close()
    if confirm==True:
        rescaling_image()

    if confirm==False:
        # Compute histogram
        intermediate_bins=max_value-min_value
        flattened_image = reference_image.flatten()  # Flatten to 1D for histogram
        inter_hist, inter_bins = np.histogram(flattened_image, bins=intermediate_bins, range=(min_value, max_value))  # 16-bit range

        # Plot the histogram for user to select min/max points
        plt.figure()
        plt.plot(inter_bins[:-1], inter_hist)
        plt.title("Select Min and Max Points for Histogram Normalization")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Frequency")
        plt.grid()

        # Let the user select 2 points on the graph
        selected_points = plt.ginput(2)  # Select two points on the histogram
        plt.close()  # Close the histogram plot after selection
        
        # Extract the selected min and max points
        min_value, max_value = int(selected_points[0][0]), int(selected_points[1][0])
        print(f"Selected range: Min = {min_value}, Max = {max_value}")
        
        preview_rescaled_image = np.clip(reference_image, min_value, max_value)  # Clip values outside the range
        preview_rescaled_image = (preview_rescaled_image - min_value) / (max_value - min_value)  # Normalize to 0-1
        preview_rescaled_image = img_as_ubyte(preview_rescaled_image)  # Convert to 8-bit (0-255)
        
        preview_flattened_image = preview_rescaled_image.flatten()  # Flatten to 1D for histogram
        preview_hist, preview_bins = np.histogram(preview_flattened_image, bins=256, range=(0, 255))
        
        plt.figure()
        plt.plot(preview_bins[:-1], preview_hist)
        plt.title("Select Min and Max Points for Histogram Normalization")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Frequency")
        plt.grid()
        
        confirm = messagebox.askokcancel("New Reference Points Selected", "New Reference points selected! Convert to BMP?")
        plt.close()
        if confirm:
            rescaling_image()
else:
    print("No reference image selected.")
    
    
