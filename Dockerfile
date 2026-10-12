FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /uvx /usr/local/bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first: this layer stays cached until requirements.txt changes
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Run as an unprivileged user, not root
RUN useradd --create-home --uid 1000 app

COPY . .
RUN chmod +x docker-entrypoint.sh \
    && python manage.py collectstatic --noinput \
    && mkdir -p media \
    && chown app:app media

USER app

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "ProductKrait.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
