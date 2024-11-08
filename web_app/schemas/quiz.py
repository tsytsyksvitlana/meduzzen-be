from pydantic import BaseModel


class AnswerCreate(BaseModel):
    text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    id: int | None = None
    title: str
    answers: list[AnswerCreate]


class QuizCreate(BaseModel):
    title: str
    description: str
    participation_frequency: int
    company_id: int
    questions: list[QuestionCreate]


class QuizUpdate(BaseModel):
    title: str
    description: str
    participation_frequency: int


class UserAnswerSchema(BaseModel):
    question_id: int
    answer_id: int


class QuizParticipationSchema(BaseModel):
    quiz_id: int
    user_answers: list[UserAnswerSchema]


class QuizParticipationResult(BaseModel):
    quiz_id: int
    total_questions: int
    correct_answers: int
    score_percentage: float
