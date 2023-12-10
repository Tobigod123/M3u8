FROM python:3.9

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy your Python script into the container
COPY bot.py /app/

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Run your Python script
CMD ["python", "bot.py"]

