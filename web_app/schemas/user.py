import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator
)

from web_app.config.constants import PASSWORD_REGEX
from web_app.exceptions.validation import (
    InvalidFieldException,
    InvalidPasswordException
)


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

    @field_validator("password")
    def validate_password(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise InvalidPasswordException()
        return v

    @field_validator("first_name", "last_name", mode="before")
    def validate_names(cls, value, field):
        if value and not re.match(r"^[A-Za-z]+$", value):
            raise InvalidFieldException(
                f"{field.name} must only contain alphabetic characters."
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
            raise InvalidFieldException(
                f"{field.name} must only contain alphabetic characters."
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


class UserPasswordChange(BaseModel):
    """
    Schema for user change password.
    """
    old_password: str
    new_password: str

    @field_validator("new_password")
    def validate_password(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise InvalidPasswordException()
        return v

    @model_validator(mode="before")
    def password_differ(cls, values):
        if values.get("new_password") == values.get("old_password"):
            raise InvalidFieldException(
                "New password cannot match the old one."
            )
        return values


class UserNewPassword(BaseModel):
    """
    Schema for setting password.
    """
    password: str

    @field_validator("password")
    def validate_password(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise InvalidPasswordException()
        return v


class OverallUserRating(BaseModel):
    """
    Model representing the overall rating of a user as a percentage score.
    """
    user_id: int
    overall_rating: float
