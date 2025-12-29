import streamlit as st
import psycopg2
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15000, limit=None, key="sentiment_refresh")
st.set_page_config(page_title="Crypto Sentiment Dashboard", layout="wide")

# DB connection helper
def get_connection():
    return psycopg2.connect(
        dbname="crypto_sentiment",
        user="aarush",
        password="password123",
        host="localhost",
        port=5433
    )

st.title("📈 Real-Time Crypto Sentiment Dashboard")

# Query latest rows
def load_latest_news(limit=20):
    conn = get_connection()
    df = pd.read_sql(
        f"SELECT * FROM sentiment_stream ORDER BY id DESC LIMIT {limit};",
        conn
    )
    conn.close()
    return df

df = load_latest_news()

st.subheader("📉 Rolling Sentiment Trend (Last 24 Hours)")

def load_sentiment_trend():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT
            date_trunc('minute', event_time) AS minute,
            AVG(sentiment_score) AS avg_sentiment
        FROM sentiment_stream
        WHERE event_time >= NOW() - INTERVAL '24 hours'
        GROUP BY minute
        ORDER BY minute ASC;
    """, conn)
    conn.close()
    return df

trend_df = load_sentiment_trend()

if not trend_df.empty:
    st.line_chart(trend_df, x="minute", y="avg_sentiment")
else:
    st.info("No sentiment trend data available yet.")


st.subheader("📰 Latest Sentiment-Tagged Crypto News")
st.dataframe(df)
