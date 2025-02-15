import recorder
import upload_to_s3
import tkinter as tk
from tkinter import messagebox, Entry, Button, Toplevel
import threading
import generate_presigned_URL

# Global Variables
download_link = None

def start_recording():
    """Starts screen and audio recording."""
    global is_paused, is_stopped
    is_paused = False
    is_stopped = False
    duration = int(duration_entry.get())
    
    threading.Thread(target=recorder.record_screen, args=(duration,)).start()
    threading.Thread(target=recorder.record_audio, args=(duration,)).start()
    #messagebox.showinfo("Recording", "Recording started!")

def merge_and_upload():
    """Merges audio and video, then uploads to S3 and generates download link."""
    recorder.merge_audio_video()
    #messagebox.showinfo("Merging", "Merging complete. Now uploading...")
    
    # Upload to S3
    #file_name, s3_key = upload_to_s3.upload_to_s3()
    upload_to_s3.upload_to_s3()
    
    # Generate Presigned URL
    global download_link
    #download_link = upload_to_s3.generate_presigned_url()
    download_url = generate_presigned_URL.generate_presigned_url()
    generate_presigned_URL. download_file(download_url, "Downloads")
    print(download_url)

    # Show download link
    if download_link:
        print("The presigned URL generated successfully.")
        show_download_link(download_link)
    else:
        messagebox.showerror("Error", "Failed to generate download link.")

def show_download_link(download_link):
    """Displays the download link in a pop-up with copy functionality."""
    # Create a new window for the download link
    link_window = Toplevel()
    link_window.title("Download Link")
    link_window.geometry("400x150")
    link_window.grab_set()  # Make the window modal
    link_window.focus_force()  # Force focus on this window

    # Entry widget for the link (read-only)
    link_entry = Entry(link_window, width=50)
    link_entry.insert(0, download_link)
    link_entry.config(state='readonly')  # Make it read-only
    link_entry.pack(pady=10)

    def copy_to_clipboard():
        """Copies the link to the clipboard."""
        link_window.clipboard_clear()
        link_window.clipboard_append(download_link)
        link_window.update()  # Keep the clipboard content after window is closed
        messagebox.showinfo("Copied", "Download link copied to clipboard!")

    # Copy Button
    copy_button = Button(link_window, text="Copy Link", command=copy_to_clipboard)
    copy_button.pack(pady=5)

    # Close Button
    close_button = Button(link_window, text="Close", command=link_window.destroy)
    close_button.pack(pady=5)


def gui():
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
