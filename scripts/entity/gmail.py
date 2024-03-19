from dataclasses import dataclass


@dataclass
class GmailMessage:
    id: str
    thread_id: str
    message: str
    history_id: str


def gmail_message_factory(id: str, thread_id: str, message: str, history_id: str) -> GmailMessage:
    return GmailMessage(id=id, thread_id=thread_id, message=message, history_id=history_id)
