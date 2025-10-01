# Use Python base image
FROM python

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install build deps (if needed for psycopg2)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Python can import top-level packages inside src (config, api, repos, etc.)
ENV PYTHONPATH=/app/src

COPY . .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--proxy-headers", "--forwarded-allow-ips", "*"]