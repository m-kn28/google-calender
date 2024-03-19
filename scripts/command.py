import sys
import time
import argparse

from google.oauth2 import service_account

from config.config import SERVICE_ACCOUNT_FILE_PATH, CALENDAR_ID, GOOGLE_CHROME_DRIVER_PATH, SALON_BOARD_USER_ID, SALON_BOARD_PASSWORD
from services.google_calender import get_google_calendar_service, get_calendar_events
from services.salon_board import all_register_salon_board
from lib.custom_logger import logger


def restart_script():
    # Restart Script for memory leak
    import os
    os.execv(__file__, ['python'] + sys.argv)


def check_calendar_event(service: service_account.Credentials, is_headress: bool, calendar_id: str, check_hours: int = 1, max_results: int = 10, confirm_interval: int = 60, is_restart: bool = False, restart_interval: int = 3600) -> None:
    # Check the calendar event
    start_time = time.time()

    while True:
        try:
            events = get_calendar_events(
                service=service, calendar_id=calendar_id, check_hours=check_hours, max_results=max_results)
            all_register_salon_board(driver_path=GOOGLE_CHROME_DRIVER_PATH, is_headress=is_headress,
                                     user_id=SALON_BOARD_USER_ID, password=SALON_BOARD_PASSWORD, events=events)
        except Exception as e:
            logger.error(f"Failed to get calendar events. {e}")
            continue
        time.sleep(confirm_interval)

        # Restart the script for memory leak
        if is_restart and time.time() - start_time > restart_interval:
            restart_script(interval=restart_interval)


def _argparse() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--is_headress', type=bool, default=False)
    parser.add_argument('--check_hours', type=int, default=1)
    parser.add_argument('--max_results', type=int, default=10)
    parser.add_argument('--confirm_interval', type=int, default=60)
    parser.add_argument('--is_restart', type=bool, default=False)
    parser.add_argument('--restart_interval', type=int, default=3600)
    return parser.parse_args()


if __name__ == '__main__':
    args = _argparse()

    service = get_google_calendar_service(SERVICE_ACCOUNT_FILE_PATH)
    check_calendar_event(service=service, is_headress=args.is_headress, calendar_id=CALENDAR_ID, check_hours=args.check_hours,
                         max_results=args.max_results, confirm_interval=args.confirm_interval, is_restart=args.is_restart, restart_interval=args.restart_interval)
