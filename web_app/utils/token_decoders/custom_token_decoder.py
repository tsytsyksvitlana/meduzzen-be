from datetime import datetime, timezone

from jose import jwt

from web_app.config.settings import settings
from web_app.exceptions.auth import (
    AuthorizationException,
    TokenExpiredException
)
from web_app.utils.token_decoders.token_decoder_interface import TokenDecoder


class CustomTokenDecoder(TokenDecoder):
    def decode(self, token: str) -> dict:
        payload = jwt.decode(
            token,
            settings.auth_jwt.SECRET_KEY,
            algorithms=[settings.auth_jwt.ALGORITHM]
        )
        if "sub" not in payload:
            raise AuthorizationException(detail="Invalid token")

        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            raise AuthorizationException(detail="Invalid token")

        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if exp_datetime < datetime.now(timezone.utc):
            raise TokenExpiredException()

        return payload
