FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System libraries needed by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# main.py mounts ./output, and the app writes ./uploads. Both are excluded
# by .dockerignore, so create them here (Compose will mount volumes over them)
RUN mkdir -p output uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]