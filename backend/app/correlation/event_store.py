from collections import defaultdict
from datetime import datetime, timedelta


class EventStore:
    """
    Stores recent events for correlation.
    Automatically removes expired events.
    """

    def __init__(self, window_minutes=10):

        self.default_window = timedelta(minutes=window_minutes)

        self.event_memory = defaultdict(list)

    def add_event(self, event):

        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow()

        username = event.get("username", "UNKNOWN")

        self.event_memory[username].append(event)

        self.cleanup(username)

    def cleanup(self, username):

        events = self.event_memory.get(username, [])

        if not events:
            return

        latest_time = events[-1]["timestamp"]

        self.event_memory[username] = [

            event

            for event in events

            if latest_time - event["timestamp"] <= self.default_window

        ]

    def get_events(self, username, window_minutes=None):

        events = self.event_memory.get(username, [])

        if window_minutes is None:
            return events

        if not events:
            return []

        reference_time = events[-1]["timestamp"]

        custom_window = timedelta(minutes=window_minutes)

        return [

            event

            for event in events

            if reference_time - event["timestamp"] <= custom_window

        ]

    def clear(self):

        self.event_memory.clear()