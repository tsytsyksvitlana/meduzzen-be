from web_app.exceptions.base import ObjectNotFoundException


class NotificationNotFoundException(ObjectNotFoundException):
    def __init__(self, notification_id: int):
        super().__init__(object_type="Notification", field=f"ID {notification_id}")
