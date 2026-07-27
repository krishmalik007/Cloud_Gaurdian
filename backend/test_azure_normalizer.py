from app.normalizer.azure import azure_normalizer


def test_activity_log():

    log = {

        "provider": "AZURE",

        "caller": "krish",

        "operationName": {

            "value": "Create VM"

        },

        "callerIpAddress": "20.10.10.10",

        "resourceLocation": "Central India",

        "eventTimestamp": "2026-07-27T12:00:00Z"

    }

    result = azure_normalizer.normalize(log)

    assert result["provider"] == "AZURE"
    assert result["username"] == "krish"
    assert result["event_name"] == "Create VM"
    assert result["event_type"] == "CREATE"
if __name__ == "__main__":

    test_activity_log()

    print("✅ Azure Normalizer Test Passed")