from app.correlation.correlation_engine import correlation_engine


events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    }

]


for event in events:

    alerts = correlation_engine.process_event(event)

    print(alerts)