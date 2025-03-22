#!/bin/bash

# A script to run database migrations with Alembic automatically choosing the environment

# Load the main .env file to check the environment setting
source .env

# Check the APP_ENV variable from the .env file to set the environment
if [[ "$APP_ENV" == "production" ]]; then
    echo "Running migrations in the Production environment."
elif [[ "$APP_ENV" == "test" ]]; then
    echo "Running migrations in the Test environment."
    source .testenv  # Assuming the test settings are separate
else
    echo "Unknown or unset APP_ENV variable in .env file. Please set APP_ENV to 'production' or 'test'."
    exit 1
fi

# Display which database will be used
echo "Using DATABASE URL: $DATABASE_URL"

# Run migrations
alembic upgrade head
echo "Migrations completed for the $APP_ENV environment."
