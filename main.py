import recorder
import upload_to_s3
import tkinter as tk
from tkinter import messagebox, Entry, Button, Toplevel
import threading
import generate_presigned_URL

# Global Variables
download_link = None  # Stores the generated download link

def start_recording():
    """Starts screen and audio recording."""
    global is_paused, is_stopped  # Flags to control recording state
    is_paused = False
    is_stopped = False
    duration = int(duration_entry.get())
    
    threading.Thread(target=recorder.record_screen, args=(duration,)).start()
    threading.Thread(target=recorder.record_audio, args=(duration,)).start()


def merge_and_upload():  # Handles merging of audio & video, uploading, and link generation
    """Merges audio and video, then uploads to S3 and generates download link."""
    recorder.merge_audio_video()
    
    # Upload to S3
    upload_to_s3.upload_to_s3()
    
    # Generate Presigned URL
    global download_link
    download_link = generate_presigned_URL.generate_presigned_url()
    generate_presigned_URL.download_file(download_link, "Downloads")
    #print(download_url)

    # Show download link
    if download_link:  # Check if the URL generation was successful
        print("The presigned URL generated successfully.")
        show_download_link(download_link)
    else:
        messagebox.showerror("Error", "Failed to generate download link.")

def show_download_link(download_link):  # Displays the presigned URL and allows copying
    """Displays the download link in a pop-up with copy functionality."""
    link_window = Toplevel()
    link_window.title("Download Link")
    link_window.geometry("400x150")
    link_window.grab_set()
    link_window.focus_force()

    link_entry = Entry(link_window, width=100)
    link_entry.insert(0, download_link)
    link_entry.config(state='readonly')
    link_entry.pack(pady=10)

    def copy_to_clipboard():
        link_window.clipboard_clear()
        link_window.clipboard_append(download_link)
        link_window.update()
        messagebox.showinfo("Copied", "Download link copied to clipboard!")

    copy_button = Button(link_window, text="Copy Link", command=copy_to_clipboard)
    copy_button.pack(pady=5)

    close_button = Button(link_window, text="Close", command=link_window.destroy)
    close_button.pack(pady=5)


def gui():  # Sets up the main GUI window for the screen recorder
    """Sets up the GUI for the screen recorder."""
    root = tk.Tk()
    root.title("Screen Recorder")
    root.geometry("400x300")
    
    tk.Label(root, text="Enter recording duration (seconds):").pack(pady=5)
    global duration_entry
    duration_entry = tk.Entry(root)
    duration_entry.pack(pady=5)
    duration_entry.insert(0, "10")
    
    tk.Button(root, text="Start Recording", command=start_recording).pack(pady=5)
    tk.Button(root, text="Pause/Resume", command=recorder.toggle_pause).pack(pady=5)
    tk.Button(root, text="Stop", command=recorder.stop_recording).pack(pady=5)
    tk.Button(root, text="Merge and Upload", command=merge_and_upload).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    gui()
