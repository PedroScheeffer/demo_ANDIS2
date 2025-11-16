# Use a specific Python version with prebuilt wheels for pydantic-core
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install system deps (psycopg2 libpq headers) and keep image small
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# Upgrade pip tooling to ensure latest wheel resolution, then install deps
RUN python -m pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt

# Ensure Python can import top-level packages inside src (config, api, repos, etc.)
ENV PYTHONPATH=/app/src

COPY . .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--proxy-headers"]