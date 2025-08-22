#!/usr/bin/env python3
"""
S3 Connection Diagnostic Script

This script helps diagnose S3 connection issues by checking:
1. Environment variables
2. AWS credentials
3. S3 bucket accessibility
4. IAM permissions

Usage:
    docker compose exec backend python diagnose_s3.py
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
import logging

# Add the app directory to Python path
sys.path.append('/app')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION'),
        'AWS_S3_BUCKET_NAME': os.getenv('AWS_S3_BUCKET_NAME')
    }
    
    all_present = True
    for var_name, var_value in required_vars.items():
        if var_value:
            # Mask sensitive values
            if 'SECRET' in var_name or 'KEY' in var_name:
                display_value = f"{var_value[:4]}...{var_value[-4:]}" if len(var_value) > 8 else "***"
            else:
                display_value = var_value
            print(f"✓ {var_name}: {display_value}")
        else:
            print(f"✗ {var_name}: NOT SET")
            all_present = False
    
    return all_present

def test_aws_credentials():
    """Test AWS credentials by calling STS get-caller-identity"""
    print("\n" + "=" * 60)
    print("TESTING AWS CREDENTIALS")
    print("=" * 60)
    
    try:
        sts_client = boto3.client('sts')
        response = sts_client.get_caller_identity()
        print(f"✓ AWS credentials are valid")
        print(f"  Account ID: {response.get('Account', 'Unknown')}")
        print(f"  User ARN: {response.get('Arn', 'Unknown')}")
        return True
    except NoCredentialsError:
        print("✗ No AWS credentials found")
        return False
    except PartialCredentialsError:
        print("✗ Incomplete AWS credentials")
        return False
    except Exception as e:
        print(f"✗ Error testing credentials: {str(e)}")
        return False

def test_s3_connection():
    """Test S3 connection and bucket access"""
    print("\n" + "=" * 60)
    print("TESTING S3 CONNECTION")
    print("=" * 60)
    
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    region = os.getenv('AWS_REGION')
    
    if not bucket_name:
        print("✗ AWS_S3_BUCKET_NAME not set")
        return False
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region
        )
        
        print(f"Testing bucket: {bucket_name}")
        print(f"Using region: {region}")
        
        # Test 1: List objects (least restrictive)
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            print("✓ list_objects_v2: SUCCESS")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"✗ list_objects_v2: FAILED ({error_code})")
            if error_code == 'NoSuchBucket':
                print("  → Bucket does not exist")
            elif error_code == 'AccessDenied':
                print("  → Access denied - check IAM permissions")
            elif error_code == 'InvalidBucketName':
                print("  → Invalid bucket name")
        
        # Test 2: Head bucket
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print("✓ head_bucket: SUCCESS")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"✗ head_bucket: FAILED ({error_code})")
            if error_code == '403':
                print("  → Forbidden - check bucket permissions")
            elif error_code == '404':
                print("  → Bucket not found")
        
        # Test 3: Get bucket location
        try:
            response = s3_client.get_bucket_location(Bucket=bucket_name)
            bucket_region = response.get('LocationConstraint') or 'us-east-1'
            print(f"✓ get_bucket_location: SUCCESS")
            print(f"  Bucket region: {bucket_region}")
            
            if bucket_region != region:
                print(f"⚠ WARNING: Bucket region ({bucket_region}) != AWS_REGION ({region})")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"✗ get_bucket_location: FAILED ({error_code})")
        
        # Test 4: Try to upload a small test file
        try:
            test_key = "test-connection/test.txt"
            test_content = b"This is a test file for connection verification"
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            print("✓ put_object: SUCCESS")
            
            # Clean up test file
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
                print("✓ delete_object: SUCCESS")
            except:
                print("⚠ Could not delete test file")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"✗ put_object: FAILED ({error_code})")
            if error_code == 'AccessDenied':
                print("  → No write permissions")
        
        return True
        
    except Exception as e:
        print(f"✗ S3 connection failed: {str(e)}")
        return False

def print_recommendations():
    """Print troubleshooting recommendations"""
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING RECOMMENDATIONS")
    print("=" * 60)
    
    print("If you're seeing connection issues, try these steps:")
    print()
    print("1. VERIFY ENVIRONMENT VARIABLES:")
    print("   - Check that all AWS_* variables are set in your .env file")
    print("   - Ensure no extra spaces or quotes around values")
    print()
    print("2. CHECK AWS CREDENTIALS:")
    print("   - Verify your AWS Access Key ID and Secret Access Key are correct")
    print("   - Make sure the IAM user exists and is active")
    print()
    print("3. VERIFY S3 BUCKET:")
    print("   - Confirm the bucket name is correct (case-sensitive)")
    print("   - Check that the bucket exists in the specified region")
    print("   - Ensure the bucket is not in a different AWS account")
    print()
    print("4. CHECK IAM PERMISSIONS:")
    print("   Your IAM user needs these permissions:")
    print("   - s3:ListBucket")
    print("   - s3:GetObject")
    print("   - s3:PutObject")
    print("   - s3:DeleteObject")
    print()
    print("5. VERIFY REGION:")
    print("   - Ensure AWS_REGION matches your bucket's region")
    print("   - Some regions require explicit configuration")
    print()
    print("6. TEST WITH AWS CLI:")
    print("   If available, test with: aws s3 ls s3://your-bucket-name")

def main():
    """Main diagnostic function"""
    print("S3 CONNECTION DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n❌ Missing required environment variables. Please set them and try again.")
        print_recommendations()
        return
    
    # Test AWS credentials
    creds_ok = test_aws_credentials()
    
    if not creds_ok:
        print("\n❌ AWS credentials test failed.")
        print_recommendations()
        return
    
    # Test S3 connection
    s3_ok = test_s3_connection()
    
    if s3_ok:
        print("\n✅ S3 connection diagnostic completed. Check individual test results above.")
    else:
        print("\n❌ S3 connection diagnostic failed.")
        print_recommendations()

if __name__ == "__main__":
    main()
