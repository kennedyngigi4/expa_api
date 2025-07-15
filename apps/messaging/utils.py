from apps.messaging.models import Notification



def send_notification(user, title, message):
    if user:
        Notification.objects.create(
            user=user,
            title=title,
            message=message
        )



