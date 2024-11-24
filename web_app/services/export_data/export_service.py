import json

from fastapi import Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.db.postgres_helper import postgres_helper as pg_helper
from web_app.db.redis_helper import redis_helper
from web_app.exceptions.data import DataNotFoundException
from web_app.exceptions.permission import PermissionDeniedException
from web_app.exceptions.validation import InvalidFieldException
from web_app.models import User
from web_app.repositories.company_membership_repository import (
    CompanyMembershipRepository
)
from web_app.schemas.roles import Role
from web_app.utils.data_exporter import DataExporter


class ExportService:
    def __init__(self, membership_repository: CompanyMembershipRepository):
        self.membership_repository = membership_repository

    async def check_is_owner_or_admin(self, company_id: int, user: User):
        membership = await self.membership_repository.get_user_company_membership(
            company_id=company_id, user_id=user.id
        )
        if not membership or not (
                membership.role == Role.OWNER.value or membership.role == Role.ADMIN.value
        ):
            raise PermissionDeniedException()

    async def export_quiz_results_for_company(
        self, quiz_id: int, company_id: int, current_user: User, export_format: str
    ):
        await self.check_is_owner_or_admin(company_id, current_user)
        file_name = f"quiz_{quiz_id}_company_{company_id}_results"
        company_quiz_users_key = f"company:{company_id}:quiz:{quiz_id}:users"
        raw_participation_data = await redis_helper.lrange(company_quiz_users_key, 0, -1)
        if not raw_participation_data:
            raise DataNotFoundException()
        participation_data = [json.loads(entry) for entry in raw_participation_data]
        return await self._generate_export_response(participation_data, file_name, export_format)

    async def export_quiz_results_for_user(
        self, quiz_id: int, user_id: int, current_user: User, export_format: str
    ):
        if current_user.id != user_id:
            raise PermissionDeniedException()
        file_name = f"quiz_{quiz_id}_user_{user_id}_results"
        user_quiz_key = f"quiz:{quiz_id}:user:{user_id}"
        raw_participation_data = await redis_helper.get(user_quiz_key)
        if not raw_participation_data:
            raise DataNotFoundException()
        participation_data = json.loads(raw_participation_data)
        return await self._generate_export_response(participation_data, file_name, export_format)

    async def export_all_quiz_results_for_user(
        self, company_id: int, user_id: int, current_user: User, export_format: str
    ):
        await self.check_is_owner_or_admin(company_id, current_user)
        file_name = f"user_{user_id}_company_{company_id}_all_quizzes"
        user_quizzes_key = f"user:{user_id}:quizzes"
        raw_user_quizzes = await redis_helper.lrange(user_quizzes_key, 0, -1)
        if not raw_user_quizzes:
            raise DataNotFoundException()
        user_quizzes = [json.loads(entry) for entry in raw_user_quizzes]
        return await self._generate_export_response(user_quizzes, file_name, export_format)

    async def export_all_quiz_results_for_company(
        self, company_id: int, quiz_id: int, user_id: int, current_user: User, export_format: str
    ):
        await self.check_is_owner_or_admin(company_id, current_user)
        file_name = f"quiz_{quiz_id}_user_{user_id}_company_{company_id}_result"
        user_quiz_key = f"company:{company_id}:user:{user_id}:quizzes"
        raw_quiz_result = await redis_helper.get(user_quiz_key)
        if not raw_quiz_result:
            raise DataNotFoundException()
        quiz_result = json.loads(raw_quiz_result)
        return await self._generate_export_response(quiz_result, file_name, export_format)

    async def _generate_export_response(self, data, file_name: str, export_format: str):
        if export_format == "json":
            temp_file_path = DataExporter.export_to_json(data, f"{file_name}.json")
            return FileResponse(
                temp_file_path,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={file_name}.json"}
            )
        elif export_format == "csv":
            csv_data = DataExporter.export_to_csv(data, f"{file_name}.csv")
            return StreamingResponse(
                csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={file_name}.csv"}
            )
        else:
            raise InvalidFieldException("Invalid format specified. Choose 'json' or 'csv'.")


def get_export_service(
    session: AsyncSession = Depends(pg_helper.session_getter)
) -> ExportService:
    return ExportService(
        membership_repository=CompanyMembershipRepository(session),
    )
