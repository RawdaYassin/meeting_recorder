import boto3
import os
import recorder
from datetime import datetime
import time

# AWS S3 configuration
S3_BUCKET_NAME = 'ghaymah-course-bucket'
S3_FOLDER_NAME = "team1_ghayma_task/"  # Folder inside the S3 bucket
AWS_ACCESS_KEY = os.getenv("GHYAMAA_AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("GHYAMAA_AWS_SECRET_KEY")
AWS_REGION = "us-east-2"

# Ensure AWS credentials are set
if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise ValueError("AWS credentials not found! Set 'GHYAMAA_AWS_ACCESS_KEY' and 'GHYAMAA_AWS_SECRET_KEY' as environment variables.")

def get_latest_session_file():
    """Finds the latest recorded session file in the 'Sessions' directory."""
    sessions_path = os.path.abspath("Sessions")
    
    if not os.path.exists(sessions_path):
        print("Error: 'Sessions' folder does not exist.")
        return None
    
    files = [f for f in os.listdir(sessions_path) if f.endswith(".mp4")]
    
    if not files:
        print("Error: No recorded session files found.")
        return None
    
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(sessions_path, f)))
    return os.path.join(sessions_path, latest_file)



def upload_to_s3():
    """Uploads the latest recorded video to AWS S3 inside the 'Rawda/' folder."""

    file_path = get_latest_session_file()
    if not file_path:
        return  # No file found, exit function

    # Wait for any process to finish writing the file
    time.sleep(2)  

    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file.")
        return

    # Extract only the filename and generate a new S3 key
    file_name = os.path.basename(file_path)
    session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #s3_key = S3_FOLDER_NAME + f"ghayma-session-{session_time}.mp4"  # Path in S3 bucket
    s3_key = S3_FOLDER_NAME + file_name

    print(f"Uploading {file_path} to S3: s3://{S3_BUCKET_NAME}/{s3_key} ...")

    s3 = boto3.client(
        's3', 
        aws_access_key_id=AWS_ACCESS_KEY, 
        aws_secret_access_key=AWS_SECRET_KEY
    )

    try:
        with open(file_path, "rb") as f:
            s3.upload_fileobj(f, S3_BUCKET_NAME, s3_key)
        print(f"✅ Upload complete: s3://{S3_BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")



# def generate_presigned_url(expiration=3600):
#     """Generates a presigned URL for downloading an S3 object."""

#     file_path = get_latest_session_file()
#     if not file_path:
#         return  # No file found, exit function

#     # Wait for any process to finish writing the file
#     time.sleep(2)  

#     if not os.path.isfile(file_path):
#         print(f"Error: '{file_path}' is not a valid file.")
#         return

#     # Extract only the filename and generate a new S3 key
#     file_name = os.path.basename(file_path)
#     session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     #s3_key = S3_FOLDER_NAME + f"ghayma-session-{session_time}.mp4"  # Path in S3 bucket
#     s3_key = S3_FOLDER_NAME + file_name

#     print(f"Generating the presigned URL for {file_path}")
#     s3_client = boto3.client(
#         's3',
#         region_name=AWS_REGION,  # Add this line
#         aws_access_key_id=AWS_ACCESS_KEY,
#         aws_secret_access_key=AWS_SECRET_KEY
#     )
    
#     try:
#         url = s3_client.generate_presigned_url(
#             'get_object',
#             Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
#             ExpiresIn=expiration
#         )
#         return url
#     except Exception as e:
#         print(f"Error generating presigned URL: {e}")
#         return None



