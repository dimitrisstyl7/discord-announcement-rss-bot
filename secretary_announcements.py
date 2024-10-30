import os

import feedparser
import requests
from bs4 import BeautifulSoup

# Discord webhook URL
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# Function to fetch announcements using RSS feed
def fetch_announcements():
    new_announcements = []

    # URL of the RSS feed
    rss_url = "https://thales.cs.unipi.gr/modules/announcements/rss.php?c=TMG118"

    # Parse the RSS feed
    feed = feedparser.parse(rss_url)

    # Get the latest 5 announcements
    entries = feed.entries[:5]

    # Loop through each announcement and build the message
    for entry in entries:
        title = entry.title
        link = entry.link
        summary = entry.summary

        # Parse summary with BeautifulSoup
        soup = BeautifulSoup(summary, 'lxml')

        # Get summary plain text
        content = soup.get_text().replace('\xa0', ' ')

        new_announcements.append(f"**{title}**\t[🔗]({link})\n\n{content}\n\n")

    # Send the announcements to Discord channel
    for announcement in new_announcements:
        send_discord_message(announcement)


# Function to send a message to the Discord webhook
def send_discord_message(content):
    data = {
        "content": content,  # The message that will be sent to the channel
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        error = response.json()
        print(f"Failed to send message: {response.status_code} - {error}")


fetch_announcements()
