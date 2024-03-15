from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from datetime import datetime, timedelta

from lib.custom_logger import logger
from entity.calendar import CalendarEvent, calendar_event_factory


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
                                              updatedMin=time_min_rfc3339).execute()
    except Exception as e:
        logger.error(f"Error: {e}")
        return []

    events = events_result.get('items', [])
    if not events:
        logger.info('No upcoming events found.')
        return []

    logger.info(f"Found {len(events)} events in the last {check_hours} hours.")

    if len(events) > 0:
        calendar_events = [
            calendar_event_factory(e)
            for e in events
            if (e.get('start') and e.get('end')) and ('dateTime' in e['start'] and 'dateTime' in e['end'])
        ]
    else:
        calendar_events = []
    logger.info(f"Calendar Events: {calendar_events}")
    return calendar_events
