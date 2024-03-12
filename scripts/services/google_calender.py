from dataclasses import dataclass
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from datetime import datetime, timedelta

from lib.custom_logger import logger


@dataclass
class CalendarEvent:
    summary: str
    description: str
    start: str
    end: str


def calendar_event_factory(event: dict) -> CalendarEvent:
    # Create a calendar event object
    description = event.get('description', 'No description')
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    return CalendarEvent(summary=event['summary'], description=description, start=start, end=end)


def get_google_calendar_service(file_path: str) -> Resource:
    # Get the google calendar service
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    credentials = service_account.Credentials.from_service_account_file(
        file_path, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)
    return service


def get_calendar_events(service: service_account.Credentials, calendar_id: str, check_hours: int = 1, max_results: int = 10) -> list[CalendarEvent] | None:
    # Get the calendar events
    updated_min_time = datetime.utcnow() - timedelta(hours=check_hours)
    time_min_rfc3339 = updated_min_time.isoformat() + 'Z'

    try:
        events_result = service.events().list(calendarId=calendar_id, maxResults=max_results,
                                              singleEvents=True, orderBy='startTime',
                                              timeMin=time_min_rfc3339).execute()
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

    events = events_result.get('items', [])
    if not events:
        logger.info('No upcoming events found.')
        return None

    calendar_events = [
        calendar_event_factory(e) for e in events if 'dateTime' in e['start'] and 'dateTime' in e['end']
    ]
    logger.info(f"Calendar Events: {calendar_events}")
    return calendar_events
