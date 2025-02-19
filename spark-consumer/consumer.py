from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr
from kafka import KafkaConsumer
import json
from prometheus_client import start_http_server, Gauge

# Start Prometheus metrics server
start_http_server(8000)
LATENCY_GAUGE = Gauge('network_latency', 'Network Latency in ms', ['device'])
PACKET_LOSS_GAUGE = Gauge('packet_loss', 'Packet Loss Percentage', ['device'])

# Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkPrometheus") \
    .master("spark://spark:7077") \
    .getOrCreate()

# Kafka Stream
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "network_telemetry") \
    .load()

# Deserialize JSON
df = df.selectExpr("CAST(value AS STRING)").alias("json_data")

# Convert JSON to DataFrame
df = df.selectExpr(
    "json_tuple(value, 'device_id', 'latency', 'packet_loss', 'timestamp') as (device_id, latency, packet_loss, timestamp)"
).selectExpr(
    "device_id",
    "CAST(latency AS DOUBLE)",
    "CAST(packet_loss AS DOUBLE)",
    "CAST(timestamp AS DOUBLE)"
)

# Detect anomalies (e.g., latency > 80ms, packet loss > 5%)
df_filtered = df.filter((col("latency") > 80) | (col("packet_loss") > 5))

# Prometheus Update Function
def update_prometheus(df, epoch_id):
    rows = df.collect()
    for row in rows:
        LATENCY_GAUGE.labels(device=row.device_id).set(row.latency)
        PACKET_LOSS_GAUGE.labels(device=row.device_id).set(row.packet_loss)

df_filtered.writeStream.foreachBatch(update_prometheus).start().awaitTermination()
