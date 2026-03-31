# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 09:50:33 2024

@author: lamazy
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import io, img_as_ubyte
from PIL import Image
import ipywidgets as widgets
from matplotlib.widgets import RectangleSelector

# Initialize global variables for averages







# Step 1: Prompt user for material names
def get_material_names():
    dialog = tk.Tk()
    dialog.title("Material Names Input")
    tk.Label(dialog, text="Enter the name of the first material reference:").pack()
    material_1_entry = tk.Entry(dialog)
    material_1_entry.pack()
    tk.Label(dialog, text="Enter the name of the second material reference:").pack()
    material_2_entry = tk.Entry(dialog)
    material_2_entry.pack()

    def on_ok():
        
        global material_names
        material_1 = material_1_entry.get()
        material_2 = material_2_entry.get()
        
        if material_1 and material_2:
            material_names = [material_1, material_2]
            dialog.destroy()
            choose_reference_option()
        else:
            messagebox.showerror("Input Error", "Please provide names for both materials.")

    tk.Button(dialog, text="OK", command=on_ok).pack()
    dialog.mainloop()
    return material_names

# Step 2: Choose reference option
def choose_reference_option():
    dialog = tk.Tk()
    dialog.title("Choose Reference Option")

    tk.Label(dialog, text="Choose an option:").pack(pady=10)

    def use_reference_dataset():
        dialog.destroy()
        # Update filetypes to include both BMP and TIFF files
        file_path = filedialog.askopenfilename(
            title="Select Reference Dataset",
            filetypes=[("Image files", "*.tif;*.tiff;*.bmp")]  # Allow both BMP and TIFF
        )
        if file_path:
            #messagebox.showinfo("Selected Dataset", f"You selected: {file_path}")
            display_image_and_select_points(file_path,on_reference_points_selected)
            #dialog.destroy()# Display the image and allow point selection
        else:
            messagebox.showerror("No File Selected", "You must select a reference dataset.")
            return

    def enter_manually():
        dialog.destroy()
        manual_input_dialog()  # Call the manual input dialog function

    tk.Button(dialog, text="Use Reference Dataset", command=use_reference_dataset).pack(pady=5)
    tk.Button(dialog, text="Enter Manually", command=enter_manually).pack(pady=5)

    dialog.mainloop()  # Start the dialog event loop

#Function for manual input dialog
def manual_input_dialog():
    dialog = tk.Tk()
    dialog.title("Manual Input")
    tk.Label(dialog, text=f"Grayvalue of {material_names[0]}").pack()
    material_1_gv_entry = tk.Entry(dialog)
    material_1_gv_entry.pack()
    tk.Label(dialog, text=f"Grayvalue of {material_names[1]}").pack()
    material_2_gv_entry = tk.Entry(dialog)
    material_2_gv_entry.pack()

    def on_ok():
        
        global material_gvs
        material_1_gv = material_1_gv_entry.get()
        material_2_gv = material_2_gv_entry.get()
        
        if material_1_gv and material_2_gv:
            material_gvs = [material_1_gv, material_2_gv]
            global avg1, avg2
            avg1=float(material_1_gv)
            avg2=float(material_2_gv)
            dialog.destroy()
            select_new_dataset()
        else:
            messagebox.showerror("Input Error", "Please provide names for both materials.")

    tk.Button(dialog, text="OK", command=on_ok).pack()



    dialog.mainloop()  # Start the dialog event loop

# Step 2: Display image and select points
def display_image_and_select_points(image_path, callback):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    global reference_image
    reference_image=image
    global folder_path
    folder_path=image_path
    if image is None:
        messagebox.showerror("Image Error", "Could not load the image.")
        return
    
    


# Initialisation
    roi_cropped = None
    points = []

    def onselect(eclick, erelease):
        #"""Sélectionne un rectangle pour recadrer l'image."""
        global roi_cropped
        roi_selector.set_active(False)
        #roi_selector.set_active(True)
        if eclick.xdata is None or eclick.ydata is None or erelease.xdata is None or erelease.ydata is None:
            print("Erreur : Sélection invalide coordonnées none.")
            return
        # Récupérer les coordonnées du rectangle sélectionné
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)

        # S'assurer que x1 < x2 et y1 < y2
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        print(f" Coordonnées sélectionnées : ({x1}, {y1}) -> ({x2}, {y2})") 
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            print("Erreur : Sélection trop petite. Essayez à nouveau.")
            return
    # Recadrer l'image
        roi_cropped = image[y1:y2, x1:x2]
        #roi_selector.set_active(False)
        
    # Fermer la fenêtre actuelle et passer à la sélection des points
        plt.close()
        select_points()

    def select_points():
        #"""Étape 2 : Sélection des points après recadrage."""
        global roi_cropped
        global fig, ax

        if roi_cropped is None:
            print("Erreur : Aucune ROI sélectionnée.")
            return

        fig, ax = plt.subplots()
        ax.imshow(roi_cropped, cmap='gray')
        ax.set_title(f"Select 2 points for {material_names[0]}")

        def onclick(event):
            #"""Enregistre les points cliqués."""
            if event.xdata is not None and event.ydata is not None:
                points.append((int(event.xdata), int(event.ydata)))
                ax.plot(event.xdata, event.ydata, 'ro' if len(points) <= 2 else 'bo')
                fig.canvas.draw()  # Mettre à jour l'affichage

                if len(points) == 2:
                    plt.title(f"Select 2 points for material {material_names[1]}")
                elif len(points) == 4:
                    plt.close()

                    callback(roi_cropped, points)
                    

        fig.canvas.mpl_connect('button_press_event', onclick)
        
       
        plt.show()

# Étape 1 : Sélection de la ROI
    
    fig, ax = plt.subplots()
    ax.imshow(image, cmap='gray')
    
    ax.set_title("ROI Selection - Click and Drag")

    
# Activation du rectangle interactif
    
    roi_selector = RectangleSelector(ax, onselect, useblit=True,
                                 button=[1],  # Active uniquement le clic gauche
                                 minspanx=5, minspany=5,  # Taille min. du rectangle
                                 interactive=True)


    plt.show()

    
    
    
    # points = []



    # def onclick(event):
    
    #     if event.xdata is not None and event.ydata is not None:
    #         points.append((int(event.xdata), int(event.ydata)))
    #         plt.plot(event.xdata, event.ydata, 'ro' if len(points) <= 2 else 'bo')
    #         plt.draw()
    #         if len(points) == 2:
    #             plt.title(f"Select 2 points for material {material_names[1]}")
    #         elif len(points) == 4:
    #             plt.close()
    #             callback(image, points)
    

    
    # plt.imshow(image, cmap='gray')
    # plt.gca().set_navigate(True)

    # plt.figure().canvas.manager.toolbar.pan()  # Active Pan
    # plt.figure().canvas.manager.toolbar.zoom()
    
    # plt.title(f"Select 2 points for {material_names[0]}")

    # def on_key(event):
    # #Ferme la fenêtre lorsque l'utilisateur appuie sur 'Enter'."""
    #     if event.key == 'enter':
    #         plt.title("Selection started...")
    #         plt.gcf().canvas.mpl_disconnect(cid_key)  # Désactiver l'écoute du clavier
    #         plt.draw()

    # cid_key = plt.gcf().canvas.mpl_connect('key_press_event', on_key)
    # plt.gcf().canvas.mpl_connect('button_press_event',onclick)
    
    # #plt.show(block=False)
    # plt.show()
    
    

# Step 3: Process points and calculate averages
def calculate_average_gray_values(image, points):
    p1, p2, p3, p4 = points
    line1 = np.linspace(p1, p2).astype(int)
    values1 = image[line1[:, 1], line1[:, 0]]
    avg1 = np.mean(values1)
    line2 = np.linspace(p3, p4).astype(int)
    values2 = image[line2[:, 1], line2[:, 0]]
    avg2 = np.mean(values2)
    return avg1, avg2

# Step 4: Handle reference points and new dataset points
def on_reference_points_selected(image, points):
    global avg1, avg2
    avg1, avg2 = calculate_average_gray_values(image, points)
    messagebox.showinfo("Reference Averages", f"Material 1 Average: {avg1}\nMaterial 2 Average: {avg2}")
    select_new_dataset()

def select_new_dataset():
    dialog=tk.Tk()
    dialog.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Dataset to Normalize",
        filetypes=[("Image files", "*.tif;*.tiff;*.bmp")]
    )
    
    if file_path:
        dialog.destroy()
        display_image_and_select_points(file_path, on_new_points_selected)
    else:
        messagebox.showerror("No File Selected", "Please select a dataset to normalize.")
        select_new_dataset()
    dialog.mainloop()
def on_new_points_selected(image, points):
    global avg3, avg4
    avg3, avg4 = calculate_average_gray_values(image, points)
    messagebox.showinfo("New Dataset Averages", f"Material 1 Average: {avg3}\nMaterial 2 Average: {avg4}")
    global avgs
    avgs=[avg1,avg2,avg3,avg4]
    select_folder_and_normalize()

# Step 5: Normalize images in the selected folder
def calculate_scale_and_offset(avg1, avg2, avg3, avg4):
    global scale
    global offset
    scale = (avg2 - avg1) / (avg4 - avg3)
    offset = avg1 - avg3 * scale
    return scale, offset

def normalize_image(image, scale, offset):
    normalized_image = image * scale + offset
    return np.clip(normalized_image, 0, 255).astype(np.uint8)

def batch_normalize_and_export(file_path, scale, offset, reference_image):
    dialog=tk.Tk()
    dialog.withdraw()
    folder_dir = os.path.dirname(file_path)  # Get the directory of the selected file
    bmp_folder = os.path.join(folder_dir, 'Normalized')
    
    if not os.path.exists(bmp_folder):
         os.makedirs(bmp_folder)
         print(f"Created folder: {bmp_folder}")
              
    # # Step 3: Conversion process
    global i
    i=1
    for filename in os.listdir(folder_dir):
         if filename.endswith(".tif") or filename.endswith(".tiff"):
             tiff_image_path = os.path.join(folder_dir, filename)
             image = io.imread(tiff_image_path)
             normalized_image=normalize_image(image, scale, offset)
        
    #         # Save the rescaled image as BMP in the new folder
             bmp_image_path = os.path.join(bmp_folder, f"{os.path.splitext(filename)[0]}.bmp")
             Image.fromarray(normalized_image).save(bmp_image_path, format="BMP")
             i=i+1
    plt.figure()
    plt.imshow(reference_image, cmap="gray")
    plt.title("Normalized Reference Image")
    plt.show()
    
    log_folder = os.path.join(bmp_folder, 'LOG FILES')
    
    if not os.path.exists(log_folder):
         os.makedirs(log_folder)
         print(f"Created folder: {log_folder}")
    normalize_log_file( log_folder,i, material_names, avgs)
    
         
    
    confirm=messagebox.askokcancel("Conversion Completed", "Do you want to normalize another dataset with same reference?")

    if confirm:
        dialog.destroy()
        plt.close()
        select_new_dataset()
    if not confirm:
        dialog.destroy()
        plt.close()

    dialog.mainloop() 

    
def select_folder_and_normalize():
    scale, offset = calculate_scale_and_offset(avg1, avg2, avg3, avg4)
    confirm = messagebox.askokcancel("Confirm Export", "Proceed with normalization and export of all images?")
    if not confirm:
        messagebox.showinfo("Export Canceled", "No images were exported.")
        return
    #folder_path = filedialog.askdirectory(title="Select Dataset Folder")
    # if not folder_path:
    #     messagebox.showerror("Folder Selection", "No folder was selected.")
    #     return
    if confirm:
        batch_normalize_and_export(folder_path, scale, offset, reference_image)



def normalize_log_file(log_folder,number_images,material_names,avgs):
    log_file = open(f"{log_folder}/Normalization.txt", "w")
    log_file.write("===================================================================")
    log_file.write("\n||                         LOG INFORMATION                        ||")
    log_file.write("\n===================================================================")
    log_file.write(f"\nNumber of images: 	{number_images}")
    log_file.write("\nReference dataset: 	Manual entry of gray values from:") 
    log_file.write(f"\nReference Material 1: 	{material_names[0]}")
    log_file.write(f"\nReference Material 2: 	{material_names[1]}")
    log_file.write("\n===================================================================")

    log_file.write("\nReference image type: 	Manual entry of reference data")
    log_file.write("\nBefore normalization image type: 	.tif")
    log_file.write("\nAfter normalization image type: 	.bmp")
    log_file.write("\n===================================================================")

    log_file.write(f"\nReference gray value of {material_names[0]} (original): 	{avgs[0]}")
    log_file.write(f"\nReference gray value of {material_names[1]} (original): 	{avgs[1]}")

    log_file.write(f"\nBefore normalization gray value of {material_names[0]} (original): 	{avgs[2]}")
    log_file.write(f"\nBefore normalization gray value of {material_names[1]} (original): 	{avgs[3]}")

    # log_file.write(f"\nAfter normalization gray value of {material_names[0]} (original): 	83.000000")
    # log_file.write(f"\nAfter normalization gray value of {material_names[1]} (original): 	172.000000")


    log_file.write("\n===================================================================") 
    log_file.close()


material_names = get_material_names()
