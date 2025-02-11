import time
import pyautogui
import numpy as np
import cv2
import pyaudio
import wave
import subprocess
import threading
import shutil  # To check if ffmpeg is installed
import mss  # Faster screen capture than pyautogui

# Screen recording setup
SCREEN_SIZE = pyautogui.size()
FPS = 20

# Audio recording setup
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# Output file names
video_output = "screen_record.avi"
audio_output = "audio_record.wav"
final_output = "final_video.mp4"

def record_audio(duration):
    """Records audio from the microphone."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    print("Recording audio...")
    try:
        for _ in range(int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
    except Exception as e:
        print(f"Audio recording error: {e}")

    print("Audio recording complete.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(audio_output, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def record_screen(duration):
    """Records the screen using mss (faster than pyautogui)."""
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_output, fourcc, FPS, SCREEN_SIZE)

    print("Recording screen...")
    start_time = time.time()

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Capture primary screen
        while time.time() - start_time < duration:
            img = sct.grab(monitor)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            out.write(frame)

    out.release()
    print("Screen recording complete.")

def merge_audio_video():
    """Merges screen and audio recordings using FFmpeg."""
    if shutil.which("ffmpeg") is None:
        print("Error: FFmpeg is not installed. Please install it and try again.")
        return

    print("Merging audio and video using ffmpeg...")
    command = [
        "ffmpeg", "-y", "-i", video_output, "-i", audio_output, 
        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", 
        "-b:a", "192k", "-strict", "experimental", final_output
    ]
    try:
        subprocess.run(command, check=True)
        print("Merging complete.")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")

if __name__ == "__main__":
    duration = int(input("Enter recording duration in seconds: "))

    screen_thread = threading.Thread(target=record_screen, args=(duration,))
    audio_thread = threading.Thread(target=record_audio, args=(duration,))

    screen_thread.start()
    audio_thread.start()

    screen_thread.join()
    audio_thread.join()

    merge_audio_video()
