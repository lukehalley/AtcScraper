# Multi-stage build for optimized production image
FROM mcr.microsoft.com/playwright/python:v1.25.2-focal

# Create a home directory.
ARG HOME_DIR="home/atc-scraper"
RUN mkdir -p /$HOME_DIR
WORKDIR /$HOME_DIR

# Move and setup files in container.
# TODO: Review and update as needed
# TODO: Review and update as needed
COPY src/ /$HOME_DIR/src/

# TODO: Review and update as needed
# Setup python files
COPY [".env", "main.py", "requirements.txt", "/$HOME_DIR/"]
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]# Enhancement: Add more detailed documentation
