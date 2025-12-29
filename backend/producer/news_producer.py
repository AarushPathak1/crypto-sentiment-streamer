import json
import time
import feedparser
from kafka import KafkaProducer
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://bitcoinmagazine.com/.rss"
]

def clean_html(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ").strip()

def create_producer():
    return KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

def fetch_rss():
    all_items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            all_items.append(entry)
    return all_items

def format_item(entry):
    title = entry.get("title", "")
    summary_raw = entry.get("summary", "")
    summary = clean_html(summary_raw)


    sentiment = get_sentiment(title + " " + summary)

    return {
        "title": title,
        "summary": summary,
        "link": entry.get("link", ""),
        "published": entry.get("published", ""),
        "timestamp": time.time(),
        "source": entry.get("source", {}).get("title", "Unknown"),
        "sentiment_score": sentiment["score"],
        "sentiment_label": sentiment["label"]
    }


analyzer = SentimentIntensityAnalyzer()
def get_sentiment(text):
    if not text:
        return {"score": 0.0, "label": "neutral"}

    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {"score": compound, "label": label}


def run_producer():
    producer = create_producer()
    print("🚀 RSS Crypto News Producer started...")

    seen = set()

    while True:
        entries = fetch_rss()

        for entry in entries:
            uid = entry.get("id", entry.get("link"))
            if uid in seen:
                continue
            seen.add(uid)

            formatted = format_item(entry)
            producer.send("crypto_feed", formatted)
            print(f"📤 Sent: {formatted['title']}")

        time.sleep(10)

if __name__ == "__main__":
    run_producer()
