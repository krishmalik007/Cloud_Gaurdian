from app.kafka.producer import kafka_producer

sample_log = {
    "provider": "AWS",
    "eventName": "ConsoleLogin",
    "username": "admin",
    "sourceIPAddress": "192.168.1.100",
    "eventTime": "2026-07-17T18:30:00Z",
    "region": "ap-south-1"
}

kafka_producer.send_log(sample_log)
kafka_producer.flush()

print("Sample log sent successfully.")