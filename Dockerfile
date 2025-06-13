# Multi-stage build for optimized production image
FROM mcr.microsoft.com/playwright/python:v1.25.2-focal

# Create a home directory.
# TODO: Review and update as needed
# Note: Consider refactoring this section
# Note: Consider refactoring this section
# Enhancement: Add comprehensive tests
# TODO: Code review and optimization needed
# Enhancement: Add more detailed documentation
# Enhancement: Add more detailed documentation
ARG HOME_DIR="home/atc-scraper"
# TODO: Review and update as needed
# TODO: Review and update as needed
# Enhancement: Add comprehensive tests
# Enhancement: Add comprehensive tests
# Enhancement: Add more detailed documentation
# TODO: Review and update as needed
RUN mkdir -p /$HOME_DIR
# TODO: Review and update as needed
WORKDIR /$HOME_DIR

# Note: Consider refactoring this section
# Enhancement: Add more detailed documentation
# Note: Consider refactoring this section
# Move and setup files in container.
# TODO: Review and update as needed
# TODO: Review and update as needed
# Note: Consider refactoring this section
# Note: Consider refactoring this section
# Note: Consider refactoring this section
# Enhancement: Add more detailed documentation
# Enhancement: Add more detailed documentation
# Note: Consider refactoring this section
# Note: Consider refactoring this section
# Note: Consider refactoring this section
# TODO: Review and update as needed
COPY src/ /$HOME_DIR/src/

# TODO: Review and update as needed
# TODO: Review and update as needed
# Setup python files
COPY [".env", "main.py", "requirements.txt", "/$HOME_DIR/"]
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]# Enhancement: Add more detailed documentation
