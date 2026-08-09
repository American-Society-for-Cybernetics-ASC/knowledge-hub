from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from . import AuthModule


auth_router = APIRouter()


# Request schemas


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class VerifyOTPRequest(BaseModel):
    email: str
    code: str


class ConfirmTOTPRequest(BaseModel):
    email: str
    code: str


# Response schemas


class RegisterResponse(BaseModel):
    qr_uri: str
    message: str


class LoginResponse(BaseModel):
    challenge_token: str
    message: str


class VerifyOTPResponse(BaseModel):
    user_id: str
    email: str
    message: str


# Endpoints


@auth_router.post("/auth/register")
def register(
    req: RegisterRequest,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> RegisterResponse:
    """
    Register a new user account.
    Returns a QR code URI for the user to scan with their authenticator app.
    """
    try:
        qr_uri = module.register(
            email=req.email,
            password=req.password,
            display_name=req.display_name,
        )
        return RegisterResponse(
            qr_uri=qr_uri,
            message="Registration successful. Please scan the QR code with your authenticator app.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/auth/confirm-totp")
def confirm_totp(
    req: ConfirmTOTPRequest,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> dict:
    """
    Confirm the user has scanned the QR code correctly.
    Must be called after register before the user can log in.
    """
    try:
        module.confirm_totp(email=req.email, code=req.code)
        return {"message": "TOTP confirmed successfully. You can now log in."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.get("/auth/totp-setup")
def get_totp_setup(
    email: str,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> RegisterResponse:
    """
    Returns the QR code URI for a user who wants to set up TOTP later.
    Can be called after registration if the user skipped the QR code step.
    """
    try:
        qr_uri = module.get_totp_setup(email=email)
        return RegisterResponse(
            qr_uri=qr_uri, message="Scan this QR code with your authenticator app."
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@auth_router.post("/auth/login")
def login(
    req: LoginRequest,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> LoginResponse:
    """
    First step of login - verify email and password.
    Returns a challenge token to be used in the verify-otp step.
    """
    try:
        challenge_token = module.login(
            email=req.email,
            password=req.password,
        )
        return LoginResponse(
            challenge_token=challenge_token,
            message="Password verified. Please enter the One-Time Passcode.",
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.post("/auth/verify-otp")
def verify_otp(
    req: VerifyOTPRequest,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> VerifyOTPResponse:
    """
    Second step of login - verify TOTP code.
    Returns user info on success. JWT will be added in a later sprint.
    """
    try:
        result = module.verify_otp(
            email=req.email,
            code=req.code,
        )
        return VerifyOTPResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
