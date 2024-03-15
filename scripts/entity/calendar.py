from dataclasses import dataclass
from datetime import datetime


@dataclass
class CalendarEvent:
    summary: str
    description: str
    start: datetime
    end: datetime


def calendar_event_factory(event: dict) -> CalendarEvent:
    # Create a calendar event object
    description = event.get('description', 'No description')
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    return CalendarEvent(summary=event['summary'], description=description, start=start, end=end)
