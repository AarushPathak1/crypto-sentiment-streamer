from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType

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
    .add("text", StringType())
    .add("timestamp", DoubleType())
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
parsed = df.select(from_json(col("value").cast("string"), schema).alias("data"))

# Print to console
query = (
    parsed.writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", False)
    .start()
)

query.awaitTermination()
