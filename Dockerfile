FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (optional but useful for many libs)
RUN apt-get update && apt-get install -y build-essential

# Copy all project files into the container
COPY . /app

# Install Python dependencies (either requirements.txt or pyproject.toml)
RUN pip install --no-cache-dir --upgrade pip
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir .; fi

EXPOSE 8080

# Run FastAPI app (for app.py containing "app = FastAPI()")
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
