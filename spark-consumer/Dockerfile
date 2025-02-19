FROM bitnami/spark:latest
WORKDIR /app
COPY consumer.py .
RUN pip install kafka-python pyspark prometheus-client
CMD ["python", "consumer.py"]
