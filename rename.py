import os

# Define the folder where images are stored
folder_path = "Images"  # e.g., 'student_images'

# List all files in the folder
image_files = [f for f in os.listdir(folder_path) if f.endswith((".jpg", ".png", "jpeg"))]

# Sort the images by filename (optional, if you want to process them in a specific order)
image_files.sort()

# Iterate through all image files and rename them with roll numbers starting from 1
for index, filename in enumerate(image_files, start=1):
    roll_number = f"R{index:03d}"  # Format roll number with leading zeros (e.g., R001, R002, ...)
    new_filename = f"{roll_number}_{filename}"
    
    # Create the full file paths
    old_file = os.path.join(folder_path, filename)
    new_file = os.path.join(folder_path, new_filename) 
    
    # Rename the file
    os.rename(old_file, new_file)
    print(f"Renamed {filename} to {new_filename}")
