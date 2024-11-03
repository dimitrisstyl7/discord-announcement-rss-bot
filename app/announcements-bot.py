import logging
import os
import threading
from logging import getLogger

import feedparser
import requests
from bs4 import BeautifulSoup

# Discord webhook URLs
ANNOUNCEMENTS_WEBHOOK_URL = os.getenv("ANNOUNCEMENTS_WEBHOOK_URL")
ERRORS_WEBHOOK_URL = os.getenv("ERRORS_WEBHOOK_URL")

# Last announcement ID file
LAST_ANNOUNCEMENT_ID_FILE = os.getenv("LAST_ANNOUNCEMENT_ID_FILE", "/app/last_announcement_id.txt")

# RSS feed URL
RSS_URL = os.getenv("RSS_URL")

# Create a logger instance
logger = getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create the last announcement ID file if it doesn't exist
if not os.path.exists(LAST_ANNOUNCEMENT_ID_FILE):
    logger.info("Creating last announcement ID file.")
    with open(LAST_ANNOUNCEMENT_ID_FILE, "w") as f:
        f.write("-1")


# Function to save the last announcement ID to a file
def save_last_announcement_id(announcement_id):
    with open(LAST_ANNOUNCEMENT_ID_FILE, "w") as f:
        logger.info(f"Saving last announcement ID (ID: {announcement_id}) to file.")
        f.write(announcement_id)


# Function to read the last announcement ID from a file
def read_last_announcement_id():
    try:
        with open(LAST_ANNOUNCEMENT_ID_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Failed to read last announcement ID: {e}")
        send_discord_message(f"Failed to read last announcement ID: {e}", ERRORS_WEBHOOK_URL)


# Function to fetch announcements using RSS feed
def fetch_announcements():
    logger.info("Fetching announcements...")
    try:
        messages = []

        # Parse the RSS feed
        feed = feedparser.parse(RSS_URL)

        # Get the latest 5 announcements
        entries = feed.entries[:5]

        # Read the last announcement ID from a file
        last_announcement_id = read_last_announcement_id()

        # Loop through each announcement and build the message
        for i in range(len(entries)):
            entry = entries[i]
            announcement_id = entry.link.split("an_id=")[1].split("&")[0]

            # Check if the announcement is new
            if announcement_id == last_announcement_id:
                break

            if i == 0:
                # Save the last announcement ID to a file
                save_last_announcement_id(announcement_id)

            # Get announcement details
            title = entry.title
            link = entry.link
            summary = entry.summary

            # Parse summary with BeautifulSoup
            soup = BeautifulSoup(summary, 'lxml')

            # Get summary plain text
            content = soup.get_text().replace('\xa0', ' ')

            # Build the message with title, link, and content
            message = f"**{title}**\t[🔗]({link})\n\n{content}\n\n"

            # Append the message to the list
            messages.append(message)

        # Send the announcements to Discord channel
        for message in messages:
            send_discord_message(message, ANNOUNCEMENTS_WEBHOOK_URL)
    except Exception as e:
        logger.error(f"Failed to fetch announcements: {e}")
        send_discord_message(f"Failed to fetch announcements: {e}", ERRORS_WEBHOOK_URL)


# Function to send a message to a Discord webhook URL
def send_discord_message(content, webhook_url):
    data = {"content": content}
    response = requests.post(webhook_url, json=data)

    # Check if the message was not sent successfully
    if response.status_code != 204:
        error = response.json()
        logger.error(msg=f"Failed to send message: {response.status_code} - {error}")


# Function to run the job every 30 minutes
def job():
    fetch_announcements()
    seconds = 30 * 60
    threading.Timer(seconds, job).start()


# Start the job
job()
