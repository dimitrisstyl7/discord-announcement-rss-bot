import logging
import os
import threading
from logging import getLogger

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables
load_dotenv()

# Discord webhook URLs
ANNOUNCEMENTS_WEBHOOK_URL = os.getenv("ANNOUNCEMENTS_WEBHOOK_URL")
ERRORS_WEBHOOK_URL = os.getenv("ERRORS_WEBHOOK_URL")

LAST_ANNOUNCEMENT_ID_DIR = os.getenv("LAST_ANNOUNCEMENT_ID_DIR", "/app/data")
LAST_ANNOUNCEMENT_ID_FILE = os.path.join(LAST_ANNOUNCEMENT_ID_DIR, "last_announcement_id.txt")

# RSS feed URL
RSS_URL = os.getenv("RSS_URL")

# Create a logger instance
logger = getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create the last announcement ID file if it doesn't exist
if not os.path.exists(LAST_ANNOUNCEMENT_ID_FILE):
    logger.info("Creating last announcement ID file.")
    os.makedirs(LAST_ANNOUNCEMENT_ID_DIR, exist_ok=True)
    with open(LAST_ANNOUNCEMENT_ID_FILE, "w") as f:
        f.write("-1")


def save_last_announcement_id(announcement_id):
    """Save the last announcement ID to a file."""
    try:
        with open(LAST_ANNOUNCEMENT_ID_FILE, "w") as f:
            logger.info(f"Saving last announcement ID (ID: {announcement_id}) to file.")
            f.write(announcement_id)
    except Exception as e:
        logger.error(f"Failed to save last announcement ID: {e}")
        send_discord_message(f"Failed to save last announcement ID: {e}", ERRORS_WEBHOOK_URL)


def read_last_announcement_id():
    """Read the last announcement ID from a file."""
    try:
        with open(LAST_ANNOUNCEMENT_ID_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Failed to read last announcement ID: {e}")
        send_discord_message(f"Failed to read last announcement ID: {e}", ERRORS_WEBHOOK_URL)
        return "-1"


def fetch_announcements():
    """Fetch announcements using RSS feed."""
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
        for i, entry in enumerate(entries):
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
            description = entry.description

            # Parse description with BeautifulSoup
            soup = BeautifulSoup(description, 'lxml')

            # Get description plain text
            content = soup.get_text().replace('\xa0', ' ')

            # Get and format the publication date
            pub_date = datetime(*entry.published_parsed[:6]).strftime("%d/%m/%y")

            # Build the message with title, link, and content
            message = f"@everyone \n **{title} (Δημοσιεύτηκε: {pub_date})**\t[🔗]({link})\n\n{content}\n\n"

            # Append the message to the list
            messages.append(message)

        # Send the announcements to Discord channel
        for message in messages:
            send_discord_message(message, ANNOUNCEMENTS_WEBHOOK_URL)
    except Exception as e:
        logger.error(f"Failed to fetch announcements: {e}")
        send_discord_message(f"Failed to fetch announcements: {e}", ERRORS_WEBHOOK_URL)


def send_discord_message(content, webhook_url):
    """Send a message to a Discord webhook URL."""
    data = {"content": content}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message: {e}")
        send_discord_message(f"Failed to send message: {e}", ERRORS_WEBHOOK_URL)


def job():
    """Run the job every 15 minutes."""
    fetch_announcements()
    seconds = 15 * 60
    threading.Timer(seconds, job).start()


# Start the job
job()
