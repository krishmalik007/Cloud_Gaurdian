from app.parser.parser import log_parser

sample_log = {
    "provider": "AWS",
    "eventName": "ConsoleLogin",
    "username": "admin",
    "sourceIPAddress": "192.168.1.100",
    "eventTime": "2026-07-19T08:00:00Z",
    "region": "ap-south-1"
}

parsed = log_parser.parse(sample_log)

print(parsed)