import boto3
import requests
import upload_to_s3
import boto3
import os
from botocore.config import Config
from datetime import datetime
import time

def generate_presigned_url( expiration=3600):
    """Generate a presigned URL to download an S3 object."""

    file_path = upload_to_s3.get_latest_session_file()
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
    s3_key = upload_to_s3.S3_FOLDER_NAME + file_name

    # Use Signature Version 4 explicitly
    s3_config = Config(
        region_name=upload_to_s3.AWS_REGION,
        signature_version='s3v4'
    )

    s3_client = boto3.client(
        's3',
        config=s3_config,
        aws_access_key_id=upload_to_s3.AWS_ACCESS_KEY,
        aws_secret_access_key=upload_to_s3.AWS_SECRET_KEY
    )
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': upload_to_s3.S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

def download_file(url, output_path):
    """Download file using presigned URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"File downloaded successfully to: {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Download failed.\nDetails: {e}")


download_url = generate_presigned_url()
download_file(download_url, "Downloads")
print(download_url)


