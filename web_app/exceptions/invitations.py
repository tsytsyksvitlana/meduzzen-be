from web_app.exceptions.base import ObjectAlreadyExistsException


class InvitationIdAlreadyExistsException(ObjectAlreadyExistsException):
    def __init__(self, invitation_id: int):
        super().__init__(object_type="Invitation", field=f"ID {invitation_id}")
