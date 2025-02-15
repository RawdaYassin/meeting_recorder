
"""
    This script generates a presigned URL for downloading an S3 object and uses 
    the URL to download the file locally. It imports configurations and helper functions 
    from the upload_to_s3 module, ensuring consistency with the upload process.
"""

# Import necessary libraries
import boto3                 # AWS SDK for Python, used to interact with S3
import requests               # To make HTTP requests (used for downloading the file)
import upload_to_s3           # Custom module for shared S3 configurations and helper functions
from botocore.config import Config  # Allows explicit configuration of AWS client behavior
from datetime import datetime # For generating timestamps
import time                   # For introducing delays to ensure file stability
import os                     # For interacting with the operating system (e.g., file paths)


def generate_presigned_url(expiration=3600):
    """
    Generates a presigned URL for downloading the latest recorded video from S3.
    
    Args:
        expiration (int): The expiration time of the presigned URL in seconds. Default is 3600 seconds (1 hour).
    
    Returns:
        str: The presigned URL if successful, None otherwise.
    """
    # Step 1: Get the latest session file path using a helper function from upload_to_s3
    file_path = upload_to_s3.get_latest_session_file()
    if not file_path:
        return  # No file found, exit function

    # Step 2: Wait to ensure no other process is writing to the file
    time.sleep(2)  

    # Step 3: Verify that the file path is valid
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file.")
        return

    # Step 4: Extract the filename and generate the S3 key
    file_name = os.path.basename(file_path)
    s3_key = upload_to_s3.S3_FOLDER_NAME + file_name

    # Step 5: Configure S3 client to explicitly use Signature Version 4
    s3_config = Config(
        region_name=upload_to_s3.AWS_REGION,
        signature_version='s3v4'  # Ensures compatibility with modern S3 security requirements
    )

    # Step 6: Initialize S3 client with custom config and credentials
    s3_client = boto3.client(
        's3',
        config=s3_config,
        aws_access_key_id=upload_to_s3.AWS_ACCESS_KEY,
        aws_secret_access_key=upload_to_s3.AWS_SECRET_KEY
    )
    
    # Step 7: Generate the presigned URL for 'get_object' operation
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': upload_to_s3.S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration  # URL expires after the specified time
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None



def download_file(url, output_path):
    """
    Downloads a file using the given presigned URL.
    
    Args:
        url (str): The presigned URL for the S3 object.
        output_path (str): The local file path where the downloaded file will be saved.
    
    Returns:
        None
    """
    try:
        # Step 1: Send an HTTP GET request to the presigned URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Step 2: Write the content of the response to a local file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"File downloaded successfully to: {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Download failed.\nDetails: {e}")
