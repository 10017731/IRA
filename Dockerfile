# Use the official slim Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose the port Cloud Run (or Docker) will use
ENV PORT 8080

# Command to start Uvicorn serving your FastAPI app
CMD ["uvicorn", "sheet_bridge:app", "--host", "0.0.0.0", "--port", "8080"]
