import os
from dotenv import load_dotenv
from backend.app.utils.s3_storage import s3_storage
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from the backend/.env file
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

def run_s3_test():
    """
    Tests S3 programmatic access by uploading a dummy markdown file
    and generating a presigned URL for it.
    """
    logger.info("Starting S3 connection test...")

    # Ensure AWS credentials and bucket name are set
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
    aws_region = os.getenv("AWS_REGION")

    if not all([aws_access_key_id, aws_secret_access_key, aws_s3_bucket_name, aws_region]):
        logger.error("Missing AWS environment variables. Please ensure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, and AWS_REGION are set in backend/.env")
        print("S3 test failed: Missing AWS environment variables.")
        return

    test_file_content = "# Hello from S3 Test!\n\nThis is a test markdown file uploaded via boto3."
    test_object_name = "test_files/hello_s3.md"
    content_type = "text/markdown"

    print(f"Attempting to upload '{test_object_name}' to bucket '{aws_s3_bucket_name}'...")
    upload_success = s3_storage.upload_file(
        file_content=test_file_content.encode('utf-8'),
        object_name=test_object_name,
        content_type=content_type
    )

    if upload_success:
        print(f"Successfully uploaded '{test_object_name}'.")
        print(f"Attempting to generate presigned URL for '{test_object_name}'...")
        presigned_url = s3_storage.generate_presigned_url(test_object_name, expiration=300) # URL valid for 5 minutes
        
        if presigned_url:
            print(f"Successfully generated presigned URL: {presigned_url}")
            print("\nS3 test PASSED!")
            print(f"You can access the file at: {presigned_url}")
            print(f"Attempting to delete '{test_object_name}' from S3...")
            delete_success = s3_storage.delete_file(test_object_name)
            if delete_success:
                print(f"Successfully deleted '{test_object_name}'.")
            else:
                print(f"Failed to delete '{test_object_name}'. Please check S3 bucket manually.")
        else:
            print("Failed to generate presigned URL.")
            print("S3 test FAILED.")
    else:
        print("Failed to upload file to S3.")
        print("S3 test FAILED.")

if __name__ == "__main__":
    run_s3_test()
