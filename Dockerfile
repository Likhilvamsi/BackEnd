# Use official lightweight Python image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file first (for caching)
COPY requirements.txt .

RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
