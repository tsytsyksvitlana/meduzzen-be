import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.repositories.quiz_repository import QuizRepository

pytestmark = pytest.mark.anyio


async def test_get_quizzes_for_company(db_session: AsyncSession, create_test_quizzes):
    quizzes = create_test_quizzes
    company_id = quizzes[0].company_id

    quiz_repository = QuizRepository(session=db_session)

    result_quizzes = await quiz_repository.get_objs(
        company_id=company_id, skip=0, limit=10
    )

    assert len(result_quizzes) == 2

    for quiz in result_quizzes:
        assert quiz.company_id == company_id

    assert result_quizzes[0].title == "General Knowledge Quiz"
    assert result_quizzes[1].title == "Math Quiz"
