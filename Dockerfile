# Use the official lightweight Python 3.12 image
FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Copy the requirements file into the container
COPY ./backend/requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the backend code into the container
COPY ./backend /code/backend

# Create a non-root user (Strict requirement for Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Give the non-root user ownership of the /code directory 
# (This is CRITICAL so SQLite can write to the database file!)
RUN chown -R user:user /code

# Switch to the non-root user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Change working directory to where the app is located
WORKDIR /code/backend

# Hugging Face Spaces exposes port 7860 by default
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
