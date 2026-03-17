from celery import Celery
from src.mails import mail, create_message
from asgiref.sync import async_to_sync

c_app = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

c_app.config_from_object("src.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)
    print("Email sent")
