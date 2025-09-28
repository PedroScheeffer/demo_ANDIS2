# Use Python base image
FROM python

# Set working directory
WORKDIR /app

# Install tzdata package for timezone configuration
RUN apt-get update && apt-get install -y tzdata

# Set the timezone environment variable
ENV TZ=America/Montevideo

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the FastAPI port
EXPOSE 5000

# Command to run the FastAPI app with uvicorn in development mode
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload", "--log-level", "debug"]
