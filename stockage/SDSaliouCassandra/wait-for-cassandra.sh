#!/bin/sh

set -e

host="$1"
port="$2"

echo "⏳ Attente de Cassandra à $host:$port..."

while ! nc -z $host $port; do
  echo "📡 Cassandra non disponible encore..."
  sleep 3
done

echo "✅ Cassandra est prêt ! Lancement du script Python..."
exec "$@"