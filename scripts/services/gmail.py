import os.path
import base64
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.external_account_authorized_user import Credentials as ExternalAccountCredentials
from google.oauth2.credentials import Credentials as OAuth2Credentials

from entity.gmail import GmailMessage, gmail_message_factory
from lib.custom_logger import logger


def get_gmail_credential(cred_file_path: str, refresh_token_path: str) -> ExternalAccountCredentials | OAuth2Credentials:
    # Get the gmail service
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None

    if os.path.exists(refresh_token_path):
        creds = OAuth2Credentials.from_authorized_user_file(
            refresh_token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_file_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(refresh_token_path, "w") as refresh_token_path:
            refresh_token_path.write(creds.to_json())
    return creds


def get_gmail_service(cred: ExternalAccountCredentials | OAuth2Credentials) -> Resource:
    return build("gmail", "v1", credentials=cred)


def get_users_messages(service: Resource, query: str) -> list[str]:
    return service.users().messages().list(userId="me", q=query).execute()


def get_thread_messages(service: Resource, thread_id: str) -> list[str]:
    return service.users().threads().get(userId="me", id=thread_id).execute()


def get_detail_message(thread_message: dict) -> str:
    message = ""
    if 'parts' in thread_message['payload']:
        for part in thread_message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body_data = part['body']['data']
                message += base64.urlsafe_b64decode(
                    body_data.encode('ASCII')).decode('utf-8')
    else:
        body_data = thread_message["payload"]["body"]["data"]
        message += base64.urlsafe_b64decode(
            body_data.encode('ASCII')).decode('utf-8')
    gmail_message = gmail_message_factory(id=thread_message["id"], thread_id=thread_message["threadId"],
                                          message=message, history_id=thread_message["historyId"])
    return gmail_message


def get_filtered_messages(service: Resource, query: str) -> list[GmailMessage]:
    results = get_users_messages(service, query)
    messages = results.get("messages", [])

    if not messages:
        logger.info("No messages found.")
        return list()

    gmail_messages = list()
    for message in messages:
        try:
            results = get_thread_messages(
                service=service, thread_id=message["threadId"])
            thread_messages = results.get('messages', [])
        except HttpError as error:
            logger.error(f"An error occurred getting thread_messages: {error}")
            return list()

        if not thread_messages:
            logger.info(f"thread_message not found for message: {message['id']}")
            return list()

        for thread_message in thread_messages:
            try:
                gmail_message = get_detail_message(thread_message)
                gmail_messages.append(gmail_message)
                logger.info(f"Getting message: {gmail_message.id}")
            except Exception as error:
                logger.error(f"An error occurred getting message: {error}")
                continue
    return gmail_messages


def get_messages(cred_file_path: str, refresh_token_path: str, query: str) -> list[GmailMessage]:
    cred = get_gmail_credential(cred_file_path, refresh_token_path)
    service = get_gmail_service(cred)
    try:
        gmail_messages = get_filtered_messages(
            service=service, query=query)
    except HttpError as error:
        logger.error(f"An error occurred getting messages: {error}")
        return list()
    return gmail_messages
