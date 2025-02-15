
"""
    This script records both the screen and audio simultaneously, then merges 
    them into a single MP4 video file using FFmpeg. It includes:

        1. Screen recording using mss and OpenCV.
        2. Audio recording using PyAudio.
        3. Merging of audio and video using FFmpeg.
        4. Pause and stop functionalities for better control during recording.
    
    The final video is saved in a directory named Sessions.

"""

# Import necessary libraries
import time                        # For time tracking and delays
import os                          # For directory and file operations
import shutil                      # For checking and removing files
import subprocess                  # To run system commands (e.g., FFmpeg)
from datetime import datetime      # For generating timestamps in filenames
import numpy as np                 # For handling arrays (used in screen capture)
import cv2                         # OpenCV for video processing
import pyautogui                   # To get screen resolution
import pyaudio                     # For audio recording
import wave                        # To save audio as a .wav file
import mss                         # For screen capturing
from tkinter import messagebox     # To display messages to the user


# Create "Sessions" folder
SESSIONS_FOLDER = "Sessions"  # Directory to store recorded sessions
os.makedirs(SESSIONS_FOLDER, exist_ok=True)  # Create directory if it doesn't exist

# Global flags
is_paused = False  # Pause recording flag
is_stopped = False  # Stop recording flag

# Screen & Audio settings
SCREEN_SIZE = pyautogui.size()  # Screen resolution (width, height)
FPS = 20                       # Frames per second for video recording
CHUNK = 1024                   # Audio buffer size
FORMAT = pyaudio.paInt16       # Audio format: 16-bit PCM
CHANNELS = 2                   # Stereo audio recording
RATE = 44100                   # Audio sampling rate (44.1 kHz)


def toggle_pause():
    """
    Toggle the pause state for recording.
    If recording is active, this function pauses it.
    If recording is paused, this function resumes it.
    """
    global is_paused
    is_paused = not is_paused  # Inverts the current pause state

def stop_recording():
    """
    Stop the recording process by setting the stop flag.
    This flag is checked inside the recording loops to gracefully exit.
    """
    global is_stopped
    is_stopped = True  # Sets the stop flag to True

def record_audio(duration):
    """
    Record audio for the specified duration with pause and stop functionality.
    
    Args:
        duration (int): Duration of the audio recording in seconds.
    """
    global is_paused, is_stopped
    
    # Initialize PyAudio and open an audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []  # List to store audio frames
    
    start_time = time.time()  # Record start time
    while time.time() - start_time < duration:
        if is_stopped:
            break
        if is_paused:
            time.sleep(0.1)  # Short sleep to avoid CPU overuse
            continue
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)  # Append audio frames
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded audio as a temporary .wav file
    with wave.open("temp_audio_record.wav", 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def record_screen(duration):
    """
    Record the screen for the specified duration with pause and stop functionality.
    
    Args:
        duration (int): Duration of the screen recording in seconds.
    """
    global is_paused, is_stopped
    
    # Initialize OpenCV video writer with XVID codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter("temp_screen_record.avi", fourcc, FPS, SCREEN_SIZE)
    
    start_time = time.time()
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Select the primary monitor
        while time.time() - start_time < duration:
            if is_stopped:
                break
            if is_paused:
                time.sleep(0.1)
                continue
            
            img = sct.grab(monitor)  # Capture screen (mss.base.ScreenShot/PIL.Image)
            frame = np.array(img)    # Convert to numpy array
            """
            When using mss, the captured screenshot is in BGRA format:
                    Blue, Green, Red, Alpha (transparency channel).
            OpenCV's VideoWriter expects frames in BGR format:
                    Blue, Green, R (no Alpha channel)
            """
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Convert color format
            out.write(frame)         # Write frame to video file
    out.release()  # Release the video writer


def merge_audio_video():
    """
    Merge recorded audio and video into a single MP4 file using FFmpeg.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_output = os.path.join(SESSIONS_FOLDER, f"ghayma-session-{timestamp}.mp4")
    
    if shutil.which("ffmpeg") is None:
        messagebox.showerror("Error", "FFmpeg is not installed!")
        return
    """
        command = [
    "ffmpeg",            # FFmpeg executable
    "-y",                # (Optional) Overwrite output file without asking
    "-i", "temp_screen_record.avi",  # (Mandatory) Input video file
    "-i", "temp_audio_record.wav",   # (Mandatory) Input audio file
    "-c:v", "libx264",   # (Optional) Video codec: H.264 encoder
    "-preset", "ultrafast", # (Optional) Encoding speed preset
    "-pix_fmt", "yuv420p",  # (Optional) Pixel format for compatibility
    "-c:a", "aac",       # (Optional) Audio codec: Advanced Audio Coding
    "-b:a", "192k",      # (Optional) Audio bitrate
    "-strict", "experimental", # (Optional) Allow experimental features (for AAC)
    "-movflags", "+faststart", # (Optional) Optimize for streaming
    final_output         # (Mandatory) Output file path
]

    """


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

