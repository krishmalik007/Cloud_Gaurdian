from app.normalizer.gcp import gcp_normalizer


def test_audit_log():

    log = {

        "provider": "GCP",

        "timestamp": "2026-07-27T12:00:00Z",

        "protoPayload": {

            "authenticationInfo": {

                "principalEmail": "krish@gmail.com"

            },

            "methodName": "storage.objects.get"

        }

    }

    result = gcp_normalizer.normalize(log)

    assert result["provider"] == "GCP"
    assert result["username"] == "krish@gmail.com"
    assert result["event_name"] == "storage.objects.get"

if __name__ == "__main__":

    test_audit_log()

    print("✅ GCP Normalizer Test Passed")