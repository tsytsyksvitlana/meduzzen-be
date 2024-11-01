import requests
from jose import jwt

from web_app.config.settings import settings
from web_app.exceptions.auth import AuthorizationException
from web_app.utils.token_decoders.token_decoder_interface import TokenDecoder


class AuthZeroTokenDecoder(TokenDecoder):
    def decode(self, token: str) -> dict:
        jwks_url = (
            f"https://{settings.auth_zero.AUTH0_DOMAIN}/.well-known/jwks.json"
        )
        jwks = requests.get(jwks_url).json()

        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == jwt.get_unverified_header(token)['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
                break

        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[settings.auth_zero.ALGORITHM],
                audience=settings.auth_zero.AUTH0_AUDIENCE
            )
            return payload
        else:
            raise AuthorizationException(detail="Invalid token")
