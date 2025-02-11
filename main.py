
import recorder
from threading import Thread
import upload_to_s3
import threading
import tkinter as tk


def start_recording():
    global is_paused, is_stopped
    is_paused = False
    is_stopped = False
    duration = int(duration_entry.get())
    
    threading.Thread(target=recorder.record_screen, args=(duration,)).start()
    threading.Thread(target=recorder.record_audio, args=(duration,)).start()

def gui():
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
    tk.Button(root, text="Merge and Save", command=recorder.merge_audio_video).pack(pady=5)
    
    root.mainloop()



if __name__ == "__main__":
    
    gui()
    upload_to_s3.upload_to_s3()