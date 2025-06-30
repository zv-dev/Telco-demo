#!/bin/sh
set -e

host="$POSTGRES_HOST"
# shift

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
python main.py 

RABBITMQ_HOST: rabbitmq
RABBITMQ_USER: user
RABBITMQ_PASS: password 
