# Official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file to the container
COPY requirements.txt .

# Install dependencies without cache to keep the image slim
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (informative for Docker Desktop and documentation)
EXPOSE 8000

# Copy the rest of the files
COPY . .

# Default command to run when starting the container
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]