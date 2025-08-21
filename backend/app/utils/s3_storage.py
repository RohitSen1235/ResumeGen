import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION")

    def upload_file(self, file_content: bytes, object_name: str, content_type: str):
        """Uploads a file to an S3 bucket.

        :param file_content: The content of the file as bytes.
        :param object_name: S3 object name.
        :param content_type: The MIME type of the file (e.g., 'application/pdf', 'image/png').
        :return: True if file was uploaded, else False.
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_content,
                ContentType=content_type
            )
            logger.info(f"File {object_name} uploaded to {self.bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload file {object_name}: {e}")
            return False

    def generate_presigned_url(self, object_name: str, expiration: int = 3600):
        """Generate a presigned URL to share an S3 object.

        :param object_name: S3 object name.
        :param expiration: Time in seconds for the presigned URL to remain valid.
        :return: Presigned URL as string. If error, returns None.
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            logger.info(f"Presigned URL generated for {object_name}")
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
            return None

    def delete_file(self, object_name: str):
        """Deletes a file from an S3 bucket.

        :param object_name: S3 object name.
        :return: True if file was deleted, else False.
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            logger.info(f"File {object_name} deleted from {self.bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file {object_name}: {e}")
            return False

s3_storage = S3Storage()
