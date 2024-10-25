import re
from datetime import datetime
from typing import ClassVar

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserSchema(BaseModel):
    """
    Schema for user.
    """
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    created_at: datetime
    updated_at: datetime | None
    last_activity_at: datetime

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class SignInRequestModel(BaseModel):
    """
    Schema for user sign-in.
    """
    email: EmailStr
    password: str


class SignUpRequestModel(BaseModel):
    """
    Schema for user sign-up.
    """
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    password: str

    PASSWORD_REGEX: ClassVar[re.Pattern] = re.compile(
        r"^"
        r"(?=.*[a-zA-Zа-яА-Я])"
        r"(?=.*[a-zа-я])"
        r"(?=.*[A-ZА-Я])"
        r"(?=.*\d)"
        r"(?=.*[^\w\s@\"'<>\-])"
        r".{8,24}$"
    )

    @field_validator("password")
    def validate_password(cls, v):
        if not cls.PASSWORD_REGEX.match(v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be 8-24 characters long, contain digits, "
                "lowercase and uppercase letters of any alphabet, "
                "and special characters except for @, \", ', <, >.",
            )
        return v

    @field_validator("first_name", "last_name", mode="before")
    def validate_names(cls, value, field):
        if value and not re.match(r"^[A-Za-z]+$", value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field.name} must only contain alphabetic characters.",
            )
        return value


class UserUpdateRequestModel(BaseModel):
    """
    Schema for user update.
    """
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("first_name", "last_name", mode="before")
    def validate_names(cls, value, field):
        if value and not re.match(r"^[A-Za-z]+$", value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field.name} must only contain "
                       f"alphabetic characters.",
            )
        return value


class UsersListResponse(BaseModel):
    """
    Schema for listing users.
    """
    users: list[UserSchema]
    total_count: int


class UserDetailResponse(BaseModel):
    """
    Schema for user detail response.
    """
    user: UserSchema
