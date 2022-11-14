FROM mcr.microsoft.com/playwright/python:v1.25.2-focal

# Create a home directory.
ARG HOME_DIR="home/atc-scraper"
RUN mkdir -p /$HOME_DIR
WORKDIR /$HOME_DIR

# Move and setup files in container.
COPY src/ /$HOME_DIR/src/

# Setup python files
COPY [".env", "main.py", "requirements.txt", "/$HOME_DIR/"]
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]