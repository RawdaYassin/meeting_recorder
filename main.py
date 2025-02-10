import cv2
import numpy as np
import pyautogui
import time
import boto3
import moviepy
import pyaudio
from datetime import datetime
import os
import keyboard  # For key press detection

# Configuration - Set these in environment variables instead!
AWS_ACCESS_KEY = os.getenv('GHYAMAA_AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('GHYAMAA_AWS_SECRET_KEY')
BUCKET_NAME = 'ghaymaa-course-bucket'
REGION = 'eu-central-1'  # Update with your bucket's region
SESSION_PREFIX = 'ghaymaa-sessions/'  # S3 folder for recordings

def create_session_filename():
    """Generate timestamped fileqname for sessions"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"ghaymaa_session_{timestamp}.mp4"

def record_ghaymaa_session(output_file):
    """Record screen until 'q' is pressed"""
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, screen_size)

    print("🔴 Ghaymaa session recording started. Press 'q' to end session...")
    
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)
        
        if keyboard.is_pressed('q'):
            break

    out.release()
    print("⏹️ Session recording saved locally:", output_file)
    return output_file

def upload_to_ghaymaa_bucket(file_path):
    """Securely upload to Ghaymaa's S3 bucket"""
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=REGION
    )
    
    try:
        file_name = os.path.basename(file_path)
        s3_key = f"{SESSION_PREFIX}{file_name}"
        
        s3.upload_file(
            Filename=file_path,
            Bucket=BUCKET_NAME,
            Key=s3_key,
            ExtraArgs={'Metadata': {'recorded-by': 'ghaymaa-automation'}}
        )
        
        print(f"✅ Successfully uploaded to: s3://{BUCKET_NAME}/{s3_key}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False

def main():
    # Generate unique filename
    session_file = create_session_filename()
    
    # Record session
    try:
        local_recording = record_ghaymaa_session(session_file)
    except Exception as e:
        print(f"❌ Recording failed: {str(e)}")
        return

    # Upload to S3
    if upload_to_ghaymaa_bucket(local_recording):
        # Optional: Remove local file after successful upload
        # os.remove(local_recording)
        pass
    else:
        print("⚠️ Local recording preserved due to upload failure")

if __name__ == "__main__":
    main()