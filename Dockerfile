# =============================
# Stage 1: Build dependencies
# =============================
FROM python:3.10 AS builder

WORKDIR /install

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg-dev \
        git \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install into /install/python
COPY requirements.txt .
RUN pip install --prefix=/install/python --no-cache-dir -r requirements.txt

# =============================
# Stage 2: Runtime
# =============================
FROM python:3.10

# Install system libraries (only what’s needed for runtime)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libjpeg-dev \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /install/python /usr/local

# Copy the app code
COPY . /app

# Expose FastAPI port
EXPOSE 8002

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]

