# 5IC Udine news fetcher
10/09/2024
Stefano Chittaro - Kitops

## Description
This script allows for automated fetching of "NOTIZIE IN EVIDENZA" from the official website of
Istituto Comprensivo V - Udine and subsequent announcement via Telegram bot
It was developed because crucial information for parents is posted there (e.g. strikes) but the school does not provide
any way to get such information in a notification manner

## Description (ITA)
Lo script permette di catturare le "NOTIZIE IN EVIDENZA" dalla home page ufficiale del V Istituto Comprensivo do Udine (https://5icudine.edu.it)
e annunciarne la pubblicazione tramite bot Telegram.
Lo svilupo si è reso necessario dal fatto che informazioni cruciali per i genitori vengono pubblicate su tale bacheca (es. scioperi) ma non vi è
alcuno strumento messo a disposizione dall'istituzione per la ricezione in maniera passiva (es. mail o app)

## DISCLAIMER (ITA)
Il presente progetto non è in alcun modo affiliato con l'Istituto Comprensivo V di Udine, il Ministero dell'Istruzione (e del Merito, lol)
o qualsivoglia entità statale del governo Italiano.

## Requirements
- Python 3.12 or later
- Everything listed in requirements.txt

## Run locally (in Virtual Env)
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
export TELEGRAM_BOT_CHATID=<your telegram chatid>
export CSV_FILE_PATH=<path to your CSV file> # required for keeping track of already_posted newsposts
export SCHEDULE_INTERVAL_SECONDS=<number in seconds> # optional, defaults to 7200s (2h)
python app.py
```

## Run in docker
```
docker run -d -e TELEGRAM_BOT_TOKEN='<your_telegram_bot_token>' \
-e TELEGRAM_BOT_CHATID='<your telegram chatid>' \
-e CSV_FILE_PATH='<path to your CSV file>' \
-e SCHEDULE_INTERVAL_SECONDS='<number in seconds>' \
-v $(pwd)/yourfile.csv:/usr/src/app/yourfile.csv \ # in case you want persistence
stefanochittaro/5icudine_news_fetcher:1.0.0
```

# TODOs
- improve logging
- fetch article details (title, date, etc) only when shall_notify is set to 0
