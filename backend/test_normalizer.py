from app.normalizer.normalizer import log_normalizer

test_logs = [

    # AWS
    {
        "provider": "AWS",
        "username": "admin",
        "event_name": "ConsoleLogin",
        "source_ip": "192.168.1.100",
        "event_time": "2026-07-19T08:00:00Z",
        "region": "ap-south-1"
    },

    # Azure
    {
        "provider": "Azure",
        "username": "john",
        "event_name": "Microsoft.Compute/login",
        "source_ip": "10.10.10.5",
        "event_time": "2026-07-19T09:00:00Z",
        "region": "eastus"
    },

    # Linux
    {
        "provider": "Linux",
        "username": "root",
        "event_name": "SSH Login Success",
        "source_ip": "172.16.1.1",
        "event_time": "2026-07-19T10:00:00Z",
        "region": "Server"
    },

    # Windows
    {
        "provider": "Windows",
        "username": "administrator",
        "event_name": "User Authentication",
        "source_ip": "192.168.10.2",
        "event_time": "2026-07-19T11:00:00Z",
        "region": "Local"
    },

    # Unknown
    {
        "provider": "Custom",
        "username": "krish",
        "event_name": "ResetDatabase",
        "source_ip": "127.0.0.1",
        "event_time": "2026-07-19T12:00:00Z",
        "region": "Unknown"
    }

]

for i, log in enumerate(test_logs, start=1):

    print(f"\n{'=' * 60}")
    print(f"TEST CASE {i}")
    print(f"{'=' * 60}")

    normalized = log_normalizer.normalize(log)

    print("\nOriginal Log:")
    print(log)

    print("\nNormalized Log:")
    print(normalized)
    