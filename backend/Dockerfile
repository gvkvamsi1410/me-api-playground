# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Expose Flask port
EXPOSE 5000

# Seed DB automatically when container starts
CMD ["bash", "-c", "python seed.py && python app.py"]
