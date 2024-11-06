from pydantic import BaseModel


class AnswerCreate(BaseModel):
    text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    title: str
    answers: list[AnswerCreate]


class QuizCreate(BaseModel):
    title: str
    description: str
    participation_frequency: int
    company_id: int
    questions: list[QuestionCreate]
