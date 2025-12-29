from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

i = 0
while True:
    msg = {
        "title": f"Test News {i}",
        "summary": "This is only a test",
        "link": "http://example.com",
        "published": "now",
        "timestamp": time.time(),
        "source": "test",
        "sentiment_score": 0.5,
        "sentiment_label": "positive"
    }
    producer.send("crypto_feed", msg)
    print("Sent test message:", msg)
    i += 1
    time.sleep(2)
