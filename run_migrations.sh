#!/bin/bash

# Get the backend service name from docker-compose
BACKEND_SERVICE="backend"

echo "Resetting all migrations..."
docker-compose exec $BACKEND_SERVICE alembic downgrade base

echo -e "\nApplying all migrations from scratch..."
docker-compose exec $BACKEND_SERVICE alembic upgrade head

echo -e "\nFinal database revision:"
docker-compose exec $BACKEND_SERVICE alembic current

if [ $? -eq 0 ]; then
    echo -e "\nMigrations applied successfully. Final revision:"
    docker-compose exec $BACKEND_SERVICE alembic current
else
    echo -e "\nFailed to apply migrations"
    exit 1
fi
