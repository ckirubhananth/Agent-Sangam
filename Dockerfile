# Agent Sangam minimal container
FROM python:3.11-slim

WORKDIR /app

# Install system deps as needed (keep minimal)
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Default port (can be overridden by cloud platform)
ENV PORT=8000
# Expose port dynamically - cloud platforms will override PORT env var
EXPOSE $PORT

# Start the FastAPI app (app.py should start the server)
CMD ["python", "app.py"]
