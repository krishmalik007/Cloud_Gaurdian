import json
import time
from datetime import datetime, timezone
from confluent_kafka import Producer, Consumer, TopicPartition
from app.config import get_settings

settings = get_settings()


def run_tc_kafka_005():
    print("=" * 70)
    print("=== TC-KAFKA-005 START: Commit Behavior Live Test ===")
    print(f"Broker: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {settings.KAFKA_TOPIC}")
    print(f"Consumer Group: cloudguardian-consumer-group")
    print("=" * 70)

    producer = Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})

    delivered = {}

    def make_delivery_callback(label):
        def callback(err, msg):
            if err is not None:
                print(f"[ERROR] {label} delivery failed: {err}")
            else:
                delivered[label] = {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset()
                }
                print(f"[{label}] Delivered to {msg.topic()} [Partition {msg.partition()}] Offset {msg.offset()}")
        return callback

    # ----------------------------------------------------
    # Step 1: Valid Message Test
    # ----------------------------------------------------
    valid_event_1 = {
        "eventVersion": "1.11",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAEXAMPLETC005_1",
            "arn": "arn:aws:iam::195236889241:user/tc-kafka-005-valid-1",
            "accountId": "195236889241",
            "userName": "tc-kafka-005-valid-1"
        },
        "eventTime": datetime.now(timezone.utc).isoformat(),
        "eventSource": "ec2.amazonaws.com",
        "eventName": "DescribeInstances",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "192.168.1.101",
        "userAgent": "Boto3/1.28.0",
        "requestParameters": None,
        "responseElements": None,
        "requestID": f"tc-kafka-005-req1-{int(time.time())}",
        "eventID": f"tc-kafka-005-evt1-{int(time.time())}",
        "readOnly": True,
        "eventType": "AwsApiCall",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management",
        "provider": "AWS"
    }

    print("\n[Step 1] Publishing Valid Message 1...")
    producer.produce(
        topic=settings.KAFKA_TOPIC,
        value=json.dumps(valid_event_1).encode("utf-8"),
        callback=make_delivery_callback("VALID_MSG_1")
    )
    producer.flush()

    print("Waiting 3s for consumer processing & commit...")
    time.sleep(3)

    # ----------------------------------------------------
    # Step 2: Malformed Message Test (Raw unparseable JSON)
    # ----------------------------------------------------
    malformed_raw = '{"provider":"AWS","eventName":"TC-KAFKA-005"'
    print("\n[Step 2] Publishing Malformed Message (missing closing brace)...")
    producer.produce(
        topic=settings.KAFKA_TOPIC,
        value=malformed_raw.encode("utf-8"),
        callback=make_delivery_callback("MALFORMED_MSG")
    )
    producer.flush()

    print("Waiting 3s for consumer error handling & skip commit...")
    time.sleep(3)

    # ----------------------------------------------------
    # Step 3: Subsequent Valid Recovery Message
    # ----------------------------------------------------
    valid_event_2 = {
        "eventVersion": "1.11",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAEXAMPLETC005_2",
            "arn": "arn:aws:iam::195236889241:user/tc-kafka-005-valid-2",
            "accountId": "195236889241",
            "userName": "tc-kafka-005-valid-2"
        },
        "eventTime": datetime.now(timezone.utc).isoformat(),
        "eventSource": "ec2.amazonaws.com",
        "eventName": "DescribeInstances",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "192.168.1.102",
        "userAgent": "Boto3/1.28.0",
        "requestParameters": None,
        "responseElements": None,
        "requestID": f"tc-kafka-005-req2-{int(time.time())}",
        "eventID": f"tc-kafka-005-evt2-{int(time.time())}",
        "readOnly": True,
        "eventType": "AwsApiCall",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management",
        "provider": "AWS"
    }

    print("\n[Step 3] Publishing Subsequent Valid Recovery Message 2...")
    producer.produce(
        topic=settings.KAFKA_TOPIC,
        value=json.dumps(valid_event_2).encode("utf-8"),
        callback=make_delivery_callback("VALID_MSG_2")
    )
    producer.flush()

    print("Waiting 3s for consumer processing & commit...")
    time.sleep(3)

    # ----------------------------------------------------
    # Step 4: Query Broker Committed Offset for Consumer Group
    # ----------------------------------------------------
    print("\n[Step 4] Checking Broker-Level Committed Offset for 'cloudguardian-consumer-group'...")
    checker = Consumer({
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "cloudguardian-consumer-group",
        "enable.auto.commit": False
    })
    partitions = [TopicPartition(settings.KAFKA_TOPIC, 0)]
    committed_partitions = checker.committed(partitions, timeout=5.0)
    checker.close()

    committed_offset = committed_partitions[0].offset if committed_partitions else "N/A"
    print(f"Broker committed offset for partition 0: {committed_offset}")

    print("\n" + "=" * 70)
    print("SUMMARY OF DELIVERIES & COMMITS:")
    for label, info in delivered.items():
        print(f"  - {label}: topic={info['topic']}, partition={info['partition']}, offset={info['offset']}")
    print(f"  - Final Broker Committed Next-Offset: {committed_offset}")
    print("=== TC-KAFKA-005 COMPLETE ===")
    print("=" * 70)


if __name__ == "__main__":
    run_tc_kafka_005()
