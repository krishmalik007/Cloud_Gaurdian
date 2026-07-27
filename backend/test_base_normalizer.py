from app.normalizer.base import BaseNormalizer

normalizer = BaseNormalizer()


def main():

    log = {

        "provider": "AWS",
        "username": "krish",
        "eventName": "ConsoleLogin",
        "sourceIPAddress": "10.0.0.5",
        "eventTime": "2026-07-27T12:00:00Z",
        "region": "ap-south-1"

    }

    result = normalizer.normalize(log)

    assert result["provider"] == "AWS"
    assert result["username"] == "krish"
    assert result["event_name"] == "ConsoleLogin"
    assert result["event_type"] == "LOGIN"
    assert result["source_ip"] == "10.0.0.5"

    print("✅ Base Normalizer Test Passed")
    print(result)


if __name__ == "__main__":
    main()