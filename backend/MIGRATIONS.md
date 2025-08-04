# Database Migration Management

This document explains the automatic database migration system implemented for the ResumeGen application.

## Overview

The application now automatically checks and applies database migrations every time Docker containers are built and started. This ensures that your database schema is always up-to-date with the latest changes.

## How It Works

### Automatic Migration on Container Startup

When you run `docker-compose up`, the backend container will:

1. **Wait for Database**: First, it waits for the PostgreSQL database to be ready
2. **Check Migrations**: It checks if there are any pending database migrations
3. **Apply Migrations**: If migrations are found, they are automatically applied
4. **Start Application**: Once migrations are complete, the FastAPI application starts

This process is handled by the `run_migrations.py` script, which is automatically executed during container startup.

### Migration Process Details

The migration system:
- Checks if Alembic is initialized (creates `alembic_version` table if needed)
- Compares current database revision with the latest migration files
- Applies any pending migrations using `alembic upgrade head`
- Logs all migration activities for debugging
- Fails gracefully if migrations encounter errors

## Manual Migration Management

For development purposes, you can also manage migrations manually using the `migrate.py` script:

### Available Commands

```bash
# Check migration status
python migrate.py status

# Apply all pending migrations
python migrate.py upgrade

# Show migration history
python migrate.py history

# Create a new migration
python migrate.py create "description of changes"

# Downgrade to a specific revision
python migrate.py downgrade <revision_id>

# Downgrade to base (remove all migrations)
python migrate.py downgrade base
```

### Examples

```bash
# Check if there are pending migrations
python migrate.py status

# Apply all pending migrations
python migrate.py upgrade

# Create a new migration after modifying models
python migrate.py create "add user preferences table"

# View migration history
python migrate.py history
```

## Files Added/Modified

### New Files
- `run_migrations.py` - Automatic migration script used by Docker
- `migrate.py` - Manual migration management script
- `MIGRATIONS.md` - This documentation file

### Modified Files
- `Dockerfile` - Updated startup script to include migration check

## Configuration

The migration system uses the same database configuration as your application:
- Database URL is read from `app.database.SQLALCHEMY_DATABASE_URL`
- Alembic configuration is in `alembic.ini`
- Migration files are stored in `alembic/versions/`

## Troubleshooting

### Common Issues

1. **Migration Fails on Startup**
   - Check the container logs: `docker-compose logs backend`
   - Ensure database is accessible and credentials are correct
   - Verify migration files are not corrupted

2. **Database Connection Issues**
   - Ensure PostgreSQL container is running
   - Check database credentials in `.env` file
   - Verify network connectivity between containers

3. **Migration Conflicts**
   - If you have multiple developers, coordinate migration creation
   - Use `python migrate.py history` to see current state
   - Resolve conflicts by creating merge migrations if needed

### Debugging

To see detailed migration logs:
```bash
# View container logs
docker-compose logs -f backend

# Check migration status manually
docker-compose exec backend python migrate.py status
```

## Best Practices

1. **Always create migrations for model changes**
   ```bash
   python migrate.py create "descriptive message"
   ```

2. **Test migrations before deploying**
   - Test both upgrade and downgrade paths
   - Verify data integrity after migrations

3. **Backup database before major migrations**
   - Especially important for production deployments

4. **Review generated migrations**
   - Check auto-generated migration files before committing
   - Ensure they capture all intended changes

## Development Workflow

1. Make changes to your SQLAlchemy models in `app/models.py`
2. Create a new migration:
   ```bash
   python migrate.py create "description of your changes"
   ```
3. Review the generated migration file in `alembic/versions/`
4. Test the migration:
   ```bash
   python migrate.py upgrade
   ```
5. Commit both model changes and migration files
6. When others pull your changes, migrations will be applied automatically on container restart

## Production Considerations

- The automatic migration system is safe for development and staging
- For production, consider running migrations manually during maintenance windows
- Always backup your production database before applying migrations
- Monitor migration logs during deployment

## Support

If you encounter issues with the migration system:
1. Check the container logs for detailed error messages
2. Verify your database connection and credentials
3. Ensure migration files are properly formatted
4. Use the manual migration tools for debugging
