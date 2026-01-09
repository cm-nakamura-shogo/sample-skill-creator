# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY scripts/pyproject.toml scripts/uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy the application
COPY scripts/process_profile_photo.py .

# Create mount points for input/output
VOLUME ["/input", "/output"]

ENTRYPOINT ["uv", "run", "python", "process_profile_photo.py"]
CMD ["--help"]
