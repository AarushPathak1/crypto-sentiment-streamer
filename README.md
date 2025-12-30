# 🚀 Real-Time Crypto Sentiment Streaming Pipeline  
*A full end-to-end real-time data engineering + analytics system built with Kafka, Spark Structured Streaming, PostgreSQL, and Streamlit.*

---

## 📌 Overview  
This project is a **real-time crypto sentiment analytics pipeline** that continuously:

### **1. Ingests live crypto news feeds**  
- Pulls breaking crypto headlines from RSS feeds (e.g., CoinDesk, CoinTelegraph).  
- Pushes cleaned + enriched messages into **Apache Kafka** in real time.

### **2. Performs streaming sentiment analysis with PySpark**  
- Consumes Kafka events using **Spark Structured Streaming**.  
- Applies lightweight sentiment scoring with VADER.  
- Computes **rolling average sentiment windows** (e.g., 30s, 5-min).  
- Writes enriched events into **PostgreSQL** for storage + analytics.

### **3. Visualizes real-time metrics in a Streamlit dashboard**  
- Live sentiment trend line (auto-updating).  
- Latest tagged news stories with sentiment metadata.  
- Clean, dark-themed UI designed for readability.

This is a *fully functional, production-style real-time data engineering pipeline* similar to what fintech, quant, and trading companies use for event-driven analytics.

---

# 🏗 System Architecture  
```text
┌──────────────┐       ┌──────────────┐       ┌───────────────┐
│  News Feeds  │  -->  │  Kafka Topic │  -->  │  Spark Stream  │
└──────────────┘       └──────────────┘       │  + Sentiment   │
                                               │  + Aggregations│
                                               └───────┬───────┘
                                                       │
                                           ┌───────────▼───────────┐
                                           │     PostgreSQL DB      │
                                           └───────────┬───────────┘
                                                       │
                                           ┌───────────▼───────────┐
                                           │   Streamlit Dashboard  │
                                           └────────────────────────┘

```
---

# ✨ Features  
### ✔ **Real-time ingestion**  
Feeds update continuously—new stories enter Kafka automatically.

### ✔ **Sentiment Scoring**  
Each story receives:
- `sentiment_score`
- `sentiment_label` (positive / neutral / negative)

### ✔ **Windowed Rolling Averages**  
Spark computes sentiment averages over sliding windows, e.g.:

Window: 2025-12-29 15:19:00 → 15:19:30
Avg Sentiment: 0.0941


### ✔ **Persistent Storage in PostgreSQL**  
Every event is stored with:
- title  
- summary  
- link  
- published date  
- event_time  
- sentiment score + label  
- insertion timestamp  

### ✔ **Live Dashboard**  
Your Streamlit UI displays:
- Rolling sentiment trend  
- Latest sentiment-tagged articles  
- Auto-refresh option  

---

# 🧰 Tech Stack  
| Component | Technology |
|----------|------------|
| **Streaming Platform** | Apache Kafka |
| **Processing Engine** | PySpark (Structured Streaming) |
| **Sentiment Analysis** | VADER (NLTK) |
| **Database** | PostgreSQL (Dockerized) |
| **Dashboard** | Streamlit |
| **Containerization** | Docker + Docker Compose |
| **Language** | Python |

---

# 📂 Project Structure  
```text
crypto-sentiment-streamer/
│
├── backend/
│ ├── producer/
│ │ └── news_producer.py # RSS → Kafka ingestion
│ ├── spark/
│ │ └── test_kafka_stream.py # Kafka → Spark → PostgreSQL
│
├── dashboard/
│ └── app.py # Streamlit real-time dashboard
│
├── docker-compose.yml # Kafka + ZooKeeper + PostgreSQL
├── requirements.txt
└── README.md
```

---

# ⚙️ Setup Instructions  

## **1. Clone the repository**
```bash
git clone https://github.com/<your-username>/crypto-sentiment-streamer.git
cd crypto-sentiment-streamer

docker-compose up -d

cd backend/producer
python news_producer.py

cd ../spark
python test_kafka_stream.py

cd ../../dashboard
streamlit run app.py

```

Open http://localhost:8501/


Postgres header: id | title | summary | link | event_time | sentiment_score | sentiment_label | inserted_at


# 🚀 Roadmap

Twitter/Reddit streaming integration

NER-based crypto ticker extraction

FinBERT sentiment model

AWS / GCP production deployment

WebSocket-powered live updates
