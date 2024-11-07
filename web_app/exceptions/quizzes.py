from web_app.exceptions.base import ObjectNotFoundException


class QuizNotFoundException(ObjectNotFoundException):
    def __init__(self, quiz_id: int):
        super().__init__(object_type="Quiz", field=f"ID {quiz_id}")


class QuestionNotFoundException(ObjectNotFoundException):
    def __init__(self, question_id: int):
        super().__init__(object_type="Question", field=f"ID {question_id}")


class AnswerNotFoundException(ObjectNotFoundException):
    def __init__(self, answer_id: int):
        super().__init__(object_type="Answer", field=f"ID {answer_id}")
