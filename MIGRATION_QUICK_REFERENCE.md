# S3 Migration Quick Reference

## Quick Commands

### Run Migration
```bash
# Method 1: Direct execution
docker compose exec backend python migration_script.py

# Method 2: Using shell script
docker compose exec backend bash run_migration.sh
```

### Diagnose S3 Issues
```bash
# Comprehensive S3 diagnostic (recommended first step)
docker compose exec backend python diagnose_s3.py

# Basic S3 connection test
docker compose exec backend python test_scripts/test_s3_connection.py
```

### Cleanup Orphaned Data
```bash
# Check for orphaned profiles (dry run)
docker compose run --rm backend python test_scripts/cleanup_orphaned_profiles.py --dry-run

# Clean up orphaned profiles (with confirmation)
docker compose run --rm backend python test_scripts/cleanup_orphaned_profiles.py

# Clean up orphaned profiles (skip confirmation)
docker compose run --rm backend python test_scripts/cleanup_orphaned_profiles.py --confirm
```

### View Logs
```bash
# View migration log
docker compose exec backend cat /app/migration.log

# Follow log in real-time
docker compose exec backend tail -f /app/migration.log
```

## Files Created

1. **`backend/migration_script.py`** - Main migration script
2. **`backend/run_migration.sh`** - Shell wrapper script
3. **`backend/diagnose_s3.py`** - S3 connection diagnostic tool
4. **`backend/S3_MIGRATION_README.md`** - Detailed documentation
5. **`MIGRATION_QUICK_REFERENCE.md`** - This quick reference

## What Gets Migrated

### PDF Resume Files
- **From**: `profiles.resume_path` (local filesystem)
- **To**: S3 with key pattern: `users/{user_id}/uploaded_resumes/{profile_id}_{timestamp}_{filename}`
- **Database**: Updates `profiles.resume_s3_key`

### Generated Resume Content
- **From**: `resumes.content` (database text field)
- **To**: S3 with key pattern: `users/{user_id}/generated_resumes/{resume_id}/content.md`
- **Database**: Updates `resumes.content_s3_key`

## Prerequisites Checklist

- [ ] S3 bucket created and accessible
- [ ] AWS credentials configured in `.env`
- [ ] Database migrations completed (S3 key columns exist)
- [ ] Docker containers running

## Environment Variables Required

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
AWS_S3_BUCKET_NAME=your_bucket_name
```

## Safety Features

- ✅ Only migrates unmigrated records (idempotent)
- ✅ Preserves original data
- ✅ Transaction rollback on failures
- ✅ Detailed logging and error handling
- ✅ Connection verification before starting

## Troubleshooting Steps

1. **First, run the diagnostic tool:**
   ```bash
   docker compose exec backend python diagnose_s3.py
   ```

2. **Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| S3 connection failed (403 Forbidden) | Check AWS credentials and bucket permissions |
| Missing environment variables | Verify all AWS_* variables are set in `.env` |
| Database connection failed | Verify containers are running: `docker compose ps` |
| File not found | Check if local files exist at specified paths |
| Region mismatch | Ensure AWS_REGION matches bucket region |

## IAM Permissions Required

Your AWS IAM user needs these S3 permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

For detailed troubleshooting, see `backend/S3_MIGRATION_README.md`.
