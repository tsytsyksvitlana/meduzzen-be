from web_app.exceptions.base import ObjectNotFoundException


class QuizNotFoundException(ObjectNotFoundException):
    def __init__(self, quiz_id: int):
        super().__init__(object_type="Quiz", field=f"ID {quiz_id}")
