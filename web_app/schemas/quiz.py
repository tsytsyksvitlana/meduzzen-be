from datetime import datetime

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
    title: str | None
    description: str | None
    participation_frequency: int | None


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


class MonthlyQuizScore(BaseModel):
    scores: list[float]
    average: float


class QuizScoreTimeData(BaseModel):
    quiz_id: int
    scores_by_month: dict[str, MonthlyQuizScore]


class LastQuizParticipation(BaseModel):
    quiz_id: int
    quiz_title: str
    last_participation_at: datetime


class CompanyAverageScoreData(BaseModel):
    time_period: str
    average_score: float


class UserQuizDetailScoreData(BaseModel):
    quiz_id: int
    scores_by_month: dict[str, float]


class UserLastQuizAttempt(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    last_attempt_at: datetime
