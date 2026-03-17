from fastapi import APIRouter, Depends, status, BackgroundTasks
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from src.db.main import get_session
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from src.mails import mail, create_message
from src.db.redis import add_jti_to_blocklist
from src.error import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from src.config import Config
from src.celery_task import send_email
from .utils import (
    create_access_token,
    generate_passwd_hash,
    decode_token,
    verify_passwrod,
    create_url_safe_token,
    decode_url_safe_token,
)
from .dependencies import (
    RefreshTokenBearer,
    AcessTokenBearer,
    get_current_user,
    RoleChecker,
)
from .schemas import (
    UserCreateModel,
    UserModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
    PasswordRestRequestModel,
    PasswordResetConfirmModel,
)


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2


# ======================= send email=======================
@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app<h1>"
    subject = "Welcome to our app"

    send_email.delay(emails, subject, html)

    return {"message": "Email sent succsufully"}


# =======================creating user acc===========================


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(
    user_data: UserCreateModel,
    bg_task: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email

    user_exits = await user_service.user_exists(email, session)

    if user_exits:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
        <h1>Verify your Email<h1>
        <p>Please click this <a href="{link}">link</a> to verify your email<p>
        """
    emails = [email]
    subject = "Verify Your email"

    send_email.delay(emails, subject, html_message)

    return {
        "message": "Account created! check email to verify your account",
        "user": new_user,
    }


# ================verify token========================


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    # print("=======TOKEN RECEIVED========:", token)
    token_data = decode_url_safe_token(token)
    # print("==============TOKEN DATA=========:", token_data)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occurred during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# =====================login user=====================
@auth_router.post("/login")
async def logging_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_passwrod(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
            )
            refresh_token = create_access_token(  # <--- Token banane wala function
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(
                    days=REFRESH_TOKEN_EXPIRY
                ),  # 'expriy' ki spelling bhi 'expiry' check karein
            )

            return JSONResponse(
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise InvalidCredentials()


# ==================get refresh token===================
@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_Access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_Access_token})

    raise InvalidToken()


# =====================get current user ==========================


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AcessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out succesful"}, status_code=status.HTTP_200_OK
    )


# =========================step to make reset pass route =============
"""
1. PROVIDE THE EMAIL -> password reset request
2. SEND PASSWORD RESET LINK 
3. REESET PASSWORD -> password reset confirm

"""

# ===================password-reset-route===========================


@auth_router.post("/password-rest-request")
async def password_reset_request(email_data: PasswordRestRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
        <h1>Reset Your Password<h1>
        <p>Please click this <a href="{link}">link</a> to Reset your Password<p>
        """
    message = create_message(
        recipients=[email], subject="Verify your email", body=html_message
    )

    await mail.send_message(message)

    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password"
        },
        status_code=status.HTTP_200_OK,
    )


# ==================reset-account-password=================


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        passwd_hash = generate_passwd_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occurred during password reset ..!!"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
