FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY app/ ./
RUN pip install -r requirements.txt

# Run the Python script
CMD ["python", "announcements-bot.py"]