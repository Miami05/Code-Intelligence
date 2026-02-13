#!/bin/bash
set -e

echo "🔄 Running database migrations..."

# Wait for database to be ready
until psql "postgresql://codeuser:codepassword@postgres:5432/codedb" -c '\q' 2>/dev/null; do
  echo "⏳ Waiting for PostgreSQL..."
  sleep 2
done

echo "✅ PostgreSQL is ready"

# Run migrations
cd /app
alembic upgrade head

echo "✅ Migrations complete"
