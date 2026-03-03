#!/bin/bash
# Initialize PostgreSQL for n8n

set -e

# Initialize PostgreSQL data directory if needed
if [ ! -d "/var/lib/postgresql/data/base" ]; then
    echo "Initializing PostgreSQL database..."
    su - postgres -c "/usr/lib/postgresql/*/bin/initdb -D /var/lib/postgresql/data"
fi

# Start PostgreSQL
su - postgres -c "/usr/lib/postgresql/*/bin/postgres -D /var/lib/postgresql/data" &
PG_PID=$!

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
for i in {1..30}; do
    if su - postgres -c "psql -lqt" &>/dev/null; then
        echo "PostgreSQL is ready"
        break
    fi
    sleep 1
done

# Create n8n database and user if they don't exist
su - postgres -c "psql" <<-EOSQL
    SELECT 'CREATE DATABASE n8n' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'n8n')\gexec
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'n8n') THEN
            CREATE USER n8n WITH ENCRYPTED PASSWORD 'n8n';
        END IF;
    END
    \$\$;
    GRANT ALL PRIVILEGES ON DATABASE n8n TO n8n;
EOSQL

echo "PostgreSQL initialized successfully"

# Keep PostgreSQL running
wait $PG_PID