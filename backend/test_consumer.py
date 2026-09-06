from app.kafka.consumer import kafka_consumer

if __name__ == "__main__":
    kafka_consumer.start()
    kafka_consumer.consume_logs()