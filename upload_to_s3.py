
import boto3
import os
import recorder


# AWS S3 configuration
S3_BUCKET_NAME = 'ghaymaa-course-bucket'
S3_FILE_NAME = "meeting_recording.mp4"
AWS_ACCESS_KEY = os.getenv('GHYAMAA_AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('GHYAMAA_AWS_SECRET_KEY')

def upload_to_s3():
    print("Uploading to S3...")
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    s3.upload_file(recorder.final_output, S3_BUCKET_NAME, S3_FILE_NAME)
    print("Upload complete.")