import time
import pyautogui
import numpy as np
import cv2
import pyaudio
import wave
import subprocess
import shutil
import mss
import os
from datetime import datetime
from tkinter import messagebox

# Create "Sessions" folder
SESSIONS_FOLDER = "Sessions"
os.makedirs(SESSIONS_FOLDER, exist_ok=True)

# Global flags
is_paused = False
is_stopped = False

# Global parameters
final_output = ""

# Screen & Audio settings
SCREEN_SIZE = pyautogui.size()
FPS = 20
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

def toggle_pause():
    global is_paused
    is_paused = not is_paused

def stop_recording():
    global is_stopped
    is_stopped = True

def record_audio(duration):
    global is_paused, is_stopped
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    
    start_time = time.time()
    while time.time() - start_time < duration:
        if is_stopped:
            break
        if is_paused:
            time.sleep(0.1)
            continue
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    with wave.open("temp_audio_record.wav", 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def record_screen(duration):
    global is_paused, is_stopped
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter("temp_screen_record.avi", fourcc, FPS, SCREEN_SIZE)
    
    start_time = time.time()
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while time.time() - start_time < duration:
            if is_stopped:
                break
            if is_paused:
                time.sleep(0.1)
                continue
            img = sct.grab(monitor)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            out.write(frame)
    
    out.release()

def merge_audio_video():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_output = os.path.join(SESSIONS_FOLDER, f"ghayma-session-{timestamp}.mp4")
    
    if shutil.which("ffmpeg") is None:
        messagebox.showerror("Error", "FFmpeg is not installed!")
        return
    
    command = [
        "ffmpeg", "-y", "-i", "temp_screen_record.avi", "-i", "temp_audio_record.wav",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-strict", "experimental",
        "-movflags", "+faststart", final_output
    ]
    subprocess.run(command, check=True)
    os.remove("temp_screen_record.avi")
    os.remove("temp_audio_record.wav")
    messagebox.showinfo("Success", f"Recording saved as: {final_output}")

