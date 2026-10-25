import json
import time
from datetime import datetime, timezone
from confluent_kafka import Producer
from app.config import get_settings

settings = get_settings()


def run_tc_kafka_003():
    print("=== TC-KAFKA-003 START ===")
    print("Publishing malformed message directly to Kafka...")
    print(f"Topic: {settings.KAFKA_TOPIC}")
    print(f"Broker: {settings.KAFKA_BOOTSTRAP_SERVERS}")

    producer = Producer({
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS
    })

    malformed_delivery = {}

    def malformed_callback(err, msg):
        if err is not None:
            print(f"[ERROR] Malformed message delivery failed: {err}")
        else:
            malformed_delivery["topic"] = msg.topic()
            malformed_delivery["partition"] = msg.partition()
            malformed_delivery["offset"] = msg.offset()
            print(f"TC-KAFKA-003 malformed message delivered")
            print(f"topic={msg.topic()}")
            print(f"partition={msg.partition()}")
            print(f"offset={msg.offset()}")

    # 1. Direct Raw Malformed Message (Invalid JSON — intentional missing closing brace)
    malformed_raw_payload = '{"provider":"AWS","eventName":"TC-KAFKA-003"'
    producer.produce(
        topic=settings.KAFKA_TOPIC,
        value=malformed_raw_payload.encode("utf-8"),
        callback=malformed_callback
    )
    producer.flush()

    print("Waiting for Kafka consumer to process malformed message...")
    time.sleep(3)

    # 2. Direct Safe Valid Recovery Message
    print("Publishing recovery message directly to Kafka...")
    print(f"Topic: {settings.KAFKA_TOPIC}")
    print(f"Broker: {settings.KAFKA_BOOTSTRAP_SERVERS}")

    recovery_delivery = {}

    def recovery_callback(err, msg):
        if err is not None:
            print(f"[ERROR] Recovery message delivery failed: {err}")
        else:
            recovery_delivery["topic"] = msg.topic()
            recovery_delivery["partition"] = msg.partition()
            recovery_delivery["offset"] = msg.offset()
            print(f"TC-KAFKA-003 recovery message delivered")
            print(f"topic={msg.topic()}")
            print(f"partition={msg.partition()}")
            print(f"offset={msg.offset()}")

    valid_recovery_event = {
        "eventVersion": "1.11",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAEXAMPLETC003",
            "arn": "arn:aws:iam::195236889241:user/tc-kafka-003-recovery-user",
            "accountId": "195236889241",
            "userName": "tc-kafka-003-recovery-user"
        },
        "eventTime": datetime.now(timezone.utc).isoformat(),
        "eventSource": "ec2.amazonaws.com",
        "eventName": "DescribeInstances",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "192.168.1.50",
        "userAgent": "Boto3/1.28.0",
        "requestParameters": None,
        "responseElements": None,
        "requestID": f"tc-kafka-003-recovery-req-{int(time.time())}",
        "eventID": f"tc-kafka-003-recovery-evt-{int(time.time())}",
        "readOnly": True,
        "eventType": "AwsApiCall",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management",
        "provider": "AWS"
    }

    producer.produce(
        topic=settings.KAFKA_TOPIC,
        value=json.dumps(valid_recovery_event).encode("utf-8"),
        callback=recovery_callback
    )
    producer.flush()

    print("Waiting for Kafka consumer to process recovery message...")
    time.sleep(3)
    print("=== TC-KAFKA-003 COMPLETE ===")


if __name__ == "__main__":
    run_tc_kafka_003()
