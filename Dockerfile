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

# Default port
ENV PORT=8000
EXPOSE 8000

# Start the FastAPI app (app.py should start the server)
CMD ["python", "app.py"]
