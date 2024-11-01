FROM python:3.12.4

# Copy requirements.txt, Python script and .env file
ADD requirements.txt .
ADD secretary_announcements.py .
ADD .env .

# Install dependencies
RUN pip install -r requirements.txt

# Run the Python script
CMD ["python", "./secretary_announcements.py"]