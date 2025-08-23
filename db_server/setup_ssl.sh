#!/bin/bash
set -e

# Create a directory for SSL certs owned by postgres user
mkdir -p /etc/postgresql/ssl
chown postgres:postgres /etc/postgresql/ssl
chmod 700 /etc/postgresql/ssl

# Copy certificates to the new directory
cp /etc/letsencrypt/live/rsfreelance.com/fullchain.pem /etc/postgresql/ssl/server.crt
cp /etc/letsencrypt/live/rsfreelance.com/privkey.pem /etc/postgresql/ssl/server.key

# Set correct ownership and permissions for the copied files
chown postgres:postgres /etc/postgresql/ssl/server.crt /etc/postgresql/ssl/server.key
chmod 600 /etc/postgresql/ssl/server.crt /etc/postgresql/ssl/server.key

# Check if SSL is already configured to avoid duplicate entries
if ! grep -q "ssl = on" /var/lib/postgresql/data/postgresql.conf; then
  echo "ssl = on" >> /var/lib/postgresql/data/postgresql.conf
  echo "ssl_cert_file = '/etc/postgresql/ssl/server.crt'" >> /var/lib/postgresql/data/postgresql.conf
  echo "ssl_key_file = '/etc/postgresql/ssl/server.key'" >> /var/lib/postgresql/data/postgresql.conf
fi

# Enforce SSL for remote connections if not already enforced
if ! grep -q "hostssl" /var/lib/postgresql/data/pg_hba.conf; then
  sed -i 's/^host    all             all             all                 scram-sha-256/hostssl all             all             all                 scram-sha-256/' /var/lib/postgresql/data/pg_hba.conf
fi

echo "PostgreSQL SSL configuration complete."
