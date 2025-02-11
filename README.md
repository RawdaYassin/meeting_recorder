# Meeting Recorder with S3 Upload
This project is a screen and audio recorder that saves recordings locally and automatically uploads them to AWS S3 inside a specified folder.

[Features]
  - Records screen and audio simultaneously.
  - Saves recordings in the Sessions/ folder with timestamps.
  - Uploads the final video to an AWS S3 bucket in a specific subfolder.
  - Pause & Resume functionality.
  - Stop recording anytime.

[How to Use] \n
    1] Run the Recorder
      - python main.py
      - Enter the recording duration in seconds.
      - Press Pause to temporarily stop, Resume to continue.
      - Press Stop to end the recording.\n
    2] Upload to S3
      - The recording is automatically uploaded to S3 inside the team1_ghayma_task/ folder.

[Folder Structure]
   meeting_recorder/
   │── Sessions/                # Recorded video files
   │── recorder.py              # Handles screen & audio recording
   │── upload_to_s3.py          # Handles AWS S3 upload
   │── main.py                  # Entry point for recording
   │── README.md                # Project documentation

[Possible Troubleshooting]
   "AWS credentials not found!"
   "Permission Denied" when uploading to S3
   "FFmpeg not found"
