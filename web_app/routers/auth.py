from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from jose import JWTError, jwt

from web_app.config.settings import settings
from web_app.schemas.token import Token
from web_app.schemas.user import SignInRequestModel

router = APIRouter()


def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.auth_jwt.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.auth_jwt.SECRET_KEY,
        algorithm=settings.auth_jwt.ALGORITHM
    )


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=401, detail="Authorization header missing"
        )

    token_type, _, token = authorization.partition(" ")
    if token_type.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401, detail="Invalid authorization header"
        )

    try:
        payload = jwt.decode(
            token,
            settings.auth_jwt.SECRET_KEY,
            algorithms=[settings.auth_jwt.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=Token)
async def login(user: SignInRequestModel):
    if user.email == "testuser@example.com" and user.password == "testpass":
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "Bearer"}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
