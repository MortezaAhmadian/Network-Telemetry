from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(bootstrap_servers='kafka:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

TOPIC = "network_telemetry"

def generate_telemetry():
    return {
        "device_id": f"router_{random.randint(1,5)}",
        "latency": round(random.uniform(1, 100), 2),  # in ms
        "packet_loss": round(random.uniform(0, 10), 2),  # in percentage
        "timestamp": time.time()
    }

while True:
    telemetry_data = generate_telemetry()
    print(f"Sending: {telemetry_data}")
    producer.send(TOPIC, telemetry_data)
    time.sleep(1)  # 1-second interval
