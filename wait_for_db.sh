#!/bin/sh

# wait for PostgreSQL to start
while ! nc -z db 5432; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done

echo "PostgreSQL is up and running!"
