import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk, filedialog

class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Download Automator")
        self.root.geometry("500x300")
        
        # Default paths (removed Archives and Programs)
        self.folder_paths = {
            "Downloads": os.path.expanduser("D:/Download_automator/downloads"),
            "Images": os.path.expanduser("C:/Users/REDTECH/Pictures"),
            "Videos": os.path.expanduser("C:/Users/REDTECH/Videos"),
            "Documents": os.path.expanduser("C:/Users/REDTECH/Documents"),
            "Music": os.path.expanduser("C:/Users/REDTECH/Music")
        }
        
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create folder selection widgets
        row = 0
        for category in self.folder_paths:
            ttk.Label(main_frame, text=f"{category} Folder:").grid(row=row, column=0, pady=5, sticky=tk.W)
            
            entry = ttk.Entry(main_frame, width=40)
            entry.insert(0, self.folder_paths[category])
            entry.grid(row=row, column=1, pady=5, padx=5)
            self.entries[category] = entry
            
            ttk.Button(main_frame, text="Browse", 
                      command=lambda c=category: self.browse_folder(c)).grid(row=row, column=2, pady=5)
            row += 1

        # Start button
        ttk.Button(main_frame, text="Start Monitoring", command=self.start_monitoring).grid(
            row=row, column=1, pady=20)

    def browse_folder(self, category):
        folder = filedialog.askdirectory(initialdir=self.entries[category].get())
        if folder:
            self.entries[category].delete(0, tk.END)
            self.entries[category].insert(0, folder)
            self.folder_paths[category] = folder

    def start_monitoring(self):
        # Update folder paths from entries
        for category in self.folder_paths:
            self.folder_paths[category] = self.entries[category].get()
        
        # Start the monitoring
        self.root.destroy()  # Close GUI
        start_file_monitoring(self.folder_paths)

TEMP_EXTENSIONS = ['.crdownload', '.part', '.tmp']

def ensure_directory_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def move_file(file_path, sorted_folders):
    if not os.path.isfile(file_path):
        return
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in TEMP_EXTENSIONS:
        print(f"Skipping temporary file: {file_path}")
        return
    
    print(f"Checking file: {file_path}")
    
    retries = 5
    while retries > 0:
        try:
            for category, folder_path in sorted_folders.items():
                if category == "Downloads":  # Skip the source folder
                    continue
                ensure_directory_exists(folder_path)
                if category == "Images" and file_extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".avif"]:
                    shutil.move(file_path, folder_path)
                    print(f"Moved {file_path} to {folder_path}")
                    return
                elif category == "Videos" and file_extension in [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"]:
                    shutil.move(file_path, folder_path)
                    print(f"Moved {file_path} to {folder_path}")
                    return
                elif category == "Documents" and file_extension in [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx"]:
                    shutil.move(file_path, folder_path)
                    print(f"Moved {file_path} to {folder_path}")
                    return
                elif category == "Music" and file_extension in [".mp3", ".wav", ".aac", ".flac"]:
                    shutil.move(file_path, folder_path)
                    print(f"Moved {file_path} to {folder_path}")
                    return
            else:
                print(f"No category matched for {file_path} with extension {file_extension}")
            break
        except PermissionError:
            retries -= 1
            time.sleep(1)
    else:
        print(f"Failed to move {file_path} after retries")

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, sorted_folders):
        self.sorted_folders = sorted_folders
    
    def on_created(self, event):
        if not event.is_directory:
            move_file(event.src_path, self.sorted_folders)
    
    def on_modified(self, event):
        if not event.is_directory:
            move_file(event.src_path, self.sorted_folders)

def start_file_monitoring(sorted_folders):
    event_handler = DownloadHandler(sorted_folders)
    observer = Observer()
    observer.schedule(event_handler, sorted_folders["Downloads"], recursive=False)
    observer.start()
    print(f"Monitoring {sorted_folders['Downloads']} for new files...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSorterGUI(root)
    root.mainloop()