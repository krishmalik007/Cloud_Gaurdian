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
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    }

]


for i, event in enumerate(events, start=1):

    alerts = correlation_engine.process_event(event)

    print(f"\n========== Event {i} ==========")

    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("No Alerts")