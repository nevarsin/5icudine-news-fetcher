# 5IC Udine news fetcher
# 10/09/2024
# Stefano Chittaro - Kitops

# This script allows for automated fetching of "NOTIZIE IN EVIDENZA" from the official website of
# Istituto Comprensivo V - Udine and subsequent announcement via Telegram bot
# It was developed because crucial information for parents is posted there (e.g. strikes) but the school does not provide
# any way to get such information in a notification manner

import sys
import requests
import re
import io
import os
import threading
import time
import datetime
from bs4 import BeautifulSoup

def log(message):
    print(f'[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {message}')

# Dynamic configuration
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.environ.get("TELEGRAM_BOT_CHATID")
csv_file_path = os.environ.get("CSV_FILE_PATH")
file_path = os.environ.get("FILE_PATH")
schedule_interval = int(os.getenv("SCHEDULE_INTERVAL_SECONDS", 7200))

# Check required parameters
if not telegram_bot_token:
    log("Missing TELEGRAM_BOT_TOKEN environment variable. Please provide a value for that")
    sys.exit(-1)

if not telegram_chat_id:
    log("Missing TELEGRAM_BOT_CHATID environment variable. Please provide a value for that")
    sys.exit(-2)

if csv_file_path:
    file_path = csv_file_path
    log("WARNING: CSV_FILE_PATH environment variable is now OBSOLETE. Please use FILE_PATH instead")

if not file_path:
    file_path = "records.txt"
    log("No storage file selected. Using 'records.txt'. All records will be deleted along with container")

# Avoid interval less than 2 hours. No need to spam that server
if schedule_interval < 7200:
    schedule_interval = 7200

# Static configuration
school_url = 'https://5icudine.edu.it'
telegram_url = f'https://api.telegram.org/bot{telegram_bot_token}/sendPhoto'

# Define task schedulation
def schedule_task():
    while True:
        news_fetch()
        time.sleep(schedule_interval)

# Add newspost URL to a defined file
def append_record(file_path, string_to_add):
    try:
        with open(file_path, mode='a+') as file:
            print(string_to_add, file=file)
    except Exception:
        log('ERROR: Unable to write on records file')

# Check whether newspost URL is already present in the file
# meaning: it has already been announced
def add_record_if_missing(file_path, string_to_add):
    try:
        with open(file_path, mode='r') as file:
            for line in file:
                if string_to_add in line:
                    return False
    except Exception:
        log("Unable to read records file. Skipping operation")

    append_record(file_path, string_to_add)
    return True

# iterate through the found newsposts, checking they already have been announced (href present in the file)
# and, if not, send a telegram image with title and href as caption
def news_fetch():
    # Send request to fetch the HTML source from the school website
    response = requests.get(school_url)
    html_source = response.text

    # Parse the fetched HTML and filter through it to find the <div> element containing the newsposts
    soup = BeautifulSoup(html_source, 'html.parser')
    articles = soup.find_all("div", "layout-articolo2")

    log('fetching...')
    for link in reversed(articles):
        # Fetch newsposts href
        link_href = link.find('a').get('href')

        # Check whether the newspost shall be notified via Telegram by checking whether the newspost href is already stored
        # in the file
        shall_notify = add_record_if_missing(file_path, link_href)

        # If this has not been notified, then prepare payload, fetch the newspost image and send the Telegram API request
        if (shall_notify):
            link_title = link.find('a').get('title')
            link_day = link.find_all("span", class_="dataGiorno")[0].get_text()
            link_month = link.find_all("span", class_="dataMese")[0].get_text()
            link_year = link.find_all("span", class_="dataAnno")[0].get_text()

            # This required regexp magic to get the image url from CSS properties
            link_image_url = re.search(r"(?P<url>https?://[^\s]+)\);", link.find_all("div", class_="immagine_post")[0].get("style")).group("url")

            params = {
                'chat_id': telegram_chat_id,
                'caption': link_title+": "+link_href,
                'parse_mode': 'html'
            }

            remote_image = requests.get(link_image_url)
            photo = io.BytesIO(remote_image.content)
            photo.name = 'img.png'

            files = {
                'photo': photo
            }
            response = requests.post(telegram_url, data=params, files=files)
            if response.status_code == 200:
                log(f'Message sent successfully: {link_title}')
            else:
                log(f'Failed to send message. Response code: {response.status_code}')
                log(response.text)

# Actual start of the task scheduler
task_thread = threading.Thread(target=schedule_task)
task_thread.start()
