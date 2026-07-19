from collections import defaultdict
from datetime import datetime, timedelta


class EventStore:
    """
    Stores recent events for correlation.
    Automatically removes old events based on a sliding time window.
    """

    def __init__(self, window_minutes=10):
        # Time window for keeping events
        self.window = timedelta(minutes=window_minutes)

        # Dictionary:
        # {
        #   "krish": [event1, event2],
        #   "john": [event3]
        # }
        self.event_memory = defaultdict(list)

    def add_event(self, event):
        """
        Add a new event to memory.
        Automatically adds timestamp if missing.
        """

        # Add timestamp if not already present
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow()

        username = event.get("username", "UNKNOWN")

        self.event_memory[username].append(event)

        # Remove expired events
        self.cleanup(username)

    def cleanup(self, username):
        """
        Remove events older than the configured time window.
        """

        current_time = datetime.utcnow()

        self.event_memory[username] = [

            event

            for event in self.event_memory[username]

            if current_time - event["timestamp"] <= self.window

        ]

    def get_events(self, username):
        """
        Return all recent events for a user.
        """

        return self.event_memory.get(username, [])

    def clear(self):
        """
        Remove all stored events.
        """

        self.event_memory.clear()