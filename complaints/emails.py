from django.core.mail import send_mail
from django.conf import settings
import threading

def send_alert(subject, message, recipients):
    """
    Sends an email in the background to avoid freezing the browser.
    """
    if not isinstance(recipients, list):
        recipients = [recipients]

    # Filter out empty emails
    valid_recipients = [r for r in recipients if r]
    
    if not valid_recipients:
        return

    def _send():
        try:
            send_mail(
                subject=f"[UrbanWatch+] {subject}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=valid_recipients,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email Error: {e}")

    # Start the background thread
    threading.Thread(target=_send).start()