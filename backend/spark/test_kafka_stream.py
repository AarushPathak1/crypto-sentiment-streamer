from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType
from pyspark.sql.functions import from_unixtime, window, col, avg

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
query2.awaitTermination()

