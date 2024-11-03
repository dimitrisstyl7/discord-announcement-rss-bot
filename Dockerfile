FROM python:3.14.0a1-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY app/requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY app/ .

# Run the Python script
CMD ["python", "./announcements_bot.py"]