from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklsit
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from typing import List
from src.db.models import User
from src.error import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,
)


user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict | None:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        if await token_in_blocklsit(token_data["jti"]):
            raise InvalidToken()

        # Ye line ab child class ka method hi chalayegi
        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data: dict):
        # Agar ye chal raha hai, matlab child class ne override nahi kiya
        raise NotImplementedError("Please override this method in child classes")


class AcessTokenBearer(TokenBearer):
    # Dhyan dein: Spelling 'verify_token_data' bilkul parent jaisi honi chahiye
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("refresh"):
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data.get("refresh"):
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AcessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):

        if not current_user.is_verified:
            raise AccountNotVerified()

        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()
