#!/bin/bash

# Get the backend service name from docker-compose
BACKEND_SERVICE="backend"
DB_SERVICE="db"

# Drop and recreate the database
echo "Resetting database..."
docker-compose exec $DB_SERVICE psql -U postgres -c "DROP DATABASE IF EXISTS resume_builder;"
docker-compose exec $DB_SERVICE psql -U postgres -c "CREATE DATABASE resume_builder WITH OWNER resume;"

# Reinitialize migrations
echo -e "\nRecreating migrations..."
docker-compose exec $BACKEND_SERVICE rm -rf alembic/versions/*
docker-compose exec $BACKEND_SERVICE alembic revision --autogenerate -m "initial migration"

# Apply migrations
echo -e "\nApplying migrations..."
docker-compose exec $BACKEND_SERVICE alembic upgrade head

echo -e "\nDatabase reset complete."
