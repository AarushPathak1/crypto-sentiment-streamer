from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType
from pyspark.sql.functions import from_unixtime, window, col, avg
import psycopg2


# Create Spark session
spark = (
    SparkSession.builder
    .appName("KafkaTestStream")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# Define schema of incoming Kafka messages
schema = (
    StructType()
    .add("title", StringType())
    .add("summary", StringType())
    .add("link", StringType())
    .add("published", StringType())
    .add("timestamp", DoubleType())
    .add("source", StringType())
    .add("sentiment_score", DoubleType())
    .add("sentiment_label", StringType())
)

# Read Kafka stream
df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "crypto_feed")
    .option("startingOffsets", "latest")
    .load()
)

# Parse JSON string into structured fields
parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

df_with_time = parsed.withColumn(
    "event_time",
    from_unixtime(col("timestamp")).cast("timestamp")
)

# 5-minute rolling average sentiment
rolling_avg = (
    df_with_time
    .withWatermark("event_time", "10 minutes")
    .groupBy(
        # window(col("event_time"), "5 minutes")
        window(col("event_time"), "30 seconds")
    )
    .agg(
        avg("sentiment_score").alias("avg_sentiment")
    )
)

def write_to_postgres(batch_df, batch_id):
    print(f">>> Writing batch {batch_id} to Postgres… rows = {batch_df.count()}")

    try:
        # Convert timestamp to string for Pandas compatibility
        safe_df = batch_df.withColumn(
            "event_time",
            col("event_time").cast("string")
        )

        pdf = safe_df.toPandas()

        if pdf.empty:
            print(">>> Empty batch, skip.")
            return

        conn = psycopg2.connect(
            dbname="crypto_sentiment",
            user="aarush",
            password="password123",
            host="localhost",
            port=5433
        )
        cur = conn.cursor()

        for _, row in pdf.iterrows():
            cur.execute("""
                INSERT INTO sentiment_stream 
                (title, summary, link, published, event_time, source, sentiment_score, sentiment_label)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row["title"],
                row["summary"],
                row["link"],
                row["published"],
                row["event_time"],   # now a string
                row["source"],
                row["sentiment_score"],
                row["sentiment_label"]
            ))

        conn.commit()
        cur.close()
        conn.close()
        print(">>> Batch inserted successfully!")

    except Exception as e:
        print(">>> ERROR writing to Postgres:", e)

postgres_query = (
    df_with_time.writeStream
    .foreachBatch(write_to_postgres)
    .outputMode("append")
    .start()
)

# # Print to console
# query = (
#     parsed.writeStream
#     .outputMode("append")
#     .format("console")
#     .option("truncate", False)
#     .start()
# )

query2 = (
    rolling_avg.writeStream
    .outputMode("update")
    .format("console")
    .option("truncate", "false")
    .start()
)

# query.awaitTermination()
# postgres_query.awaitTermination()
# query2.awaitTermination()
spark.streams.awaitAnyTermination()

