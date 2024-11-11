import asyncio
import json

import pytest
from fastapi.responses import FileResponse

from web_app.exceptions.permission import PermissionDeniedException
from web_app.services.export.export_service import ExportService

pytestmark = pytest.mark.anyio


async def test_export_quiz_results_for_company(
    db_session,
    create_test_users,
    create_test_quizzes,
    export_service,
    mock_redis,
    event_loop
):
    user = create_test_users[0]
    quiz = create_test_quizzes[0]
    company_id = quiz.company_id
    quiz_id = quiz.id

    mock_participation_data = [
        json.dumps({
            "user_id": user.id,
            "company_id": quiz.company_id,
            "quiz_id": quiz_id,
            "total_questions": 8,
            "correct_answers": 100,
            "score_percentage": 80,
        })
    ]

    mock_redis.lrange.return_value = mock_participation_data

    results = await export_service.export_quiz_results_for_company(
        quiz_id, company_id, current_user=user, export_format="json"
    )

    assert isinstance(results, FileResponse)

    assert "Content-Disposition" in results.headers
    assert "quiz_1_company_1_results.json" in results.headers["Content-Disposition"]


@pytest.mark.asyncio
async def test_export_quiz_results_for_user(
    db_session,
    create_test_users,
    create_test_quizzes,
    export_service,
    mock_redis,
    event_loop
):
    async def test():
        user = create_test_users[0]
        quiz = create_test_quizzes[0]
        quiz_id = quiz.id

        mock_participation_data = json.dumps({
            "user_id": user.id,
            "company_id": quiz.company_id,
            "quiz_id": quiz_id,
            "correct_answers": 8,
            "total_questions": 10,
            "score_percentage": 80,
        })

        mock_redis.get.return_value = mock_participation_data

        result = await export_service.export_quiz_results_for_user(
            quiz_id, user.id, current_user=user, export_format="json"
        )

        assert isinstance(result, FileResponse)
        assert "Content-Disposition" in result.headers
        assert f"quiz_{quiz_id}_user_{user.id}_results.json" in result.headers["Content-Disposition"]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test())


@pytest.mark.asyncio
async def test_export_all_quiz_results_for_user(
    db_session,
    create_test_users,
    create_test_quizzes,
    export_service,
    mock_redis,
    event_loop
):
    async def test():
        user = create_test_users[0]
        quiz = create_test_quizzes[0]
        company_id = quiz.company_id
        quiz_id = quiz.id

        mock_participation_data = [
            json.dumps({
                "user_id": user.id,
                "company_id": quiz.company_id,
                "quiz_id": quiz_id,
                "total_questions": 8,
                "correct_answers": 7,
                "score_percentage": 87.5
            })
        ]

        mock_redis.lrange.return_value = mock_participation_data

        result = await export_service.export_all_quiz_results_for_user(
            company_id, user.id, current_user=user, export_format="json"
        )

        assert isinstance(result, FileResponse)
        assert "Content-Disposition" in result.headers
        assert f"user_{user.id}_company_{company_id}_all_quizzes.json" in result.headers["Content-Disposition"]

        another_user = create_test_users[1]
        with pytest.raises(PermissionDeniedException):
            await export_service.export_all_quiz_results_for_user(
                company_id, user.id, current_user=another_user, export_format="json"
            )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test())


@pytest.mark.asyncio
async def test_export_all_quiz_results_for_company(
    db_session,
    create_test_users,
    create_test_quizzes,
    export_service: ExportService,
    mock_redis,
    event_loop
):
    async def test():
        user = create_test_users[0]
        quiz = create_test_quizzes[0]
        company_id = quiz.company_id
        quiz_id = quiz.id

        mock_quiz_result = {
            "user_id": user.id,
            "company_id": quiz.company_id,
            "quiz_id": quiz_id,
            "total_questions": 8,
            "correct_answers": 7,
            "score_percentage": 87.5,
        }
        mock_redis.get.return_value = json.dumps(mock_quiz_result)

        result = await export_service.export_all_quiz_results_for_company(
            company_id=company_id, quiz_id=quiz_id, user_id=user.id, current_user=user, export_format="json"
        )

        assert isinstance(result, FileResponse)
        assert "Content-Disposition" in result.headers
        assert f"quiz_{quiz_id}_user_{user.id}_company_{company_id}_result.json" in result.headers["Content-Disposition"]

        user_quiz_key = f"company:{company_id}:user:{user.id}:quizzes"
        mock_redis.get.assert_called_with(user_quiz_key)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test())
