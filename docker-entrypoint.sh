#!/bin/sh
set -e

# Dev migrates on start. Production runs the one-off `migrate` service instead,
# so several web containers never migrate at the same time.
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput
fi

exec "$@"
