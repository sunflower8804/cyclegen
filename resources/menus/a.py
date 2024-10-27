import os

def list_png_files(folder_path):
    try:
        # List all files in the specified folder
        files = os.listdir(folder_path)
        
        # Filter and print out only the .png files
        png_files = [file for file in files if file.lower().endswith('.png')]
        
        if png_files:
            print("PNG files in the folder:")
            for png in png_files:
                print(png[:-4])
        else:
            print("No PNG files found in the folder.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Specify the folder path
folder_path = 'resources\menus'  # Change this to your folder path
list_png_files(folder_path)
