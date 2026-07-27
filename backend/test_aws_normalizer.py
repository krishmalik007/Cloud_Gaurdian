from app.normalizer.aws import aws_normalizer


def test_cloudtrail_log():

    log = {

        "provider": "AWS",

        "eventName": "ConsoleLogin",

        "eventTime": "2026-07-27T12:00:00Z",

        "awsRegion": "ap-south-1",

        "sourceIPAddress": "10.0.0.5",

        "userIdentity": {

            "userName": "krish"

        }

    }

    result = aws_normalizer.normalize(log)

    assert result["provider"] == "AWS"
    assert result["username"] == "krish"
    assert result["event_name"] == "ConsoleLogin"
    assert result["event_type"] == "LOGIN"
    assert result["region"] == "ap-south-1"



if __name__ == "__main__":
    test_cloudtrail_log()
    print("✅ AWS Normalizer Test Passed")