
"""
    This script uploads the latest recorded video from the local Sessions 
    folder to an AWS S3 bucket. It checks for the latest .mp4 file, constructs 
    the appropriate S3 path, and then securely uploads the file using AWS 
    credentials obtained from environment variables.

"""

# Import necessary libraries
import boto3                    # AWS SDK for Python, used to interact with S3
import os                       # For interacting with the operating system (e.g., file paths, environment variables)
from datetime import datetime   # For generating timestamps
import time                     # For introducing delays to ensure file stability

# AWS S3 Configuration
S3_BUCKET_NAME = 'ghaymah-course-bucket'  # Name of the S3 bucket to upload files
S3_FOLDER_NAME = "team1_ghayma_task/"     # Folder inside the S3 bucket where files will be stored
AWS_ACCESS_KEY = os.getenv("GHYAMAA_AWS_ACCESS_KEY")  # AWS Access Key from environment variable
AWS_SECRET_KEY = os.getenv("GHYAMAA_AWS_SECRET_KEY")  # AWS Secret Key from environment variable
AWS_REGION = "us-east-2"                     # AWS region for the S3 bucket

# Ensure AWS credentials are set
if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise ValueError("AWS credentials not found! Set 'GHYAMAA_AWS_ACCESS_KEY' and 'GHYAMAA_AWS_SECRET_KEY' as environment variables.")

def get_latest_session_file():
    """
    Finds the latest recorded session file in the 'Sessions' directory.
    
    Returns:
        str: The absolute path to the latest .mp4 file in the 'Sessions' folder.
             Returns None if no valid file is found.
    """
    sessions_path = os.path.abspath("Sessions")  # Get absolute path for the 'Sessions' directory
    
    # Check if the 'Sessions' folder exists
    if not os.path.exists(sessions_path):
        print("Error: 'Sessions' folder does not exist.")
        return None
    
    # List all files ending with .mp4 in the Sessions folder
    files = [f for f in os.listdir(sessions_path) if f.endswith(".mp4")]
    
    # If no .mp4 files are found, return None
    if not files:
        print("Error: No recorded session files found.")
        return None
    
    # Find the latest file by modification time
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(sessions_path, f)))
    
    # Return the absolute path of the latest file
    return os.path.join(sessions_path, latest_file)

def upload_to_s3():
    """
    Uploads the latest recorded video to AWS S3 inside the specified folder.
    
    Steps:
        1. Finds the latest recorded session file.
        2. Verifies the file's validity.
        3. Generates a unique S3 key for the file.
        4. Uploads the file to the specified S3 bucket and folder.
    """
    # Step 1: Find the latest session file
    file_path = get_latest_session_file()
    if not file_path:
        return  # No file found, exit the function

    # Step 2: Wait for any process to finish writing to the file
    time.sleep(2)  

    # Check if the file path is a valid file
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file.")
        return

    # Step 3: Extract filename and generate a unique S3 key
    file_name = os.path.basename(file_path)
    session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    s3_key = S3_FOLDER_NAME + file_name  # Use the original filename for the S3 key

    print(f"Uploading {file_path} to S3: s3://{S3_BUCKET_NAME}/{s3_key} ...")

    # Step 4: Initialize S3 client using boto3
    s3 = boto3.client(
        's3', 
        aws_access_key_id=AWS_ACCESS_KEY, 
        aws_secret_access_key=AWS_SECRET_KEY
    )

    try:
        # Upload the file to S3
        with open(file_path, "rb") as f:
            s3.upload_fileobj(f, S3_BUCKET_NAME, s3_key)
        print(f"✅ Upload complete: s3://{S3_BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
