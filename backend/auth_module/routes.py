from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response

from . import AuthModule


auth_router = APIRouter(prefix="/auth", tags=["auth"])


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
    requires_totp: bool
    challenge_token: str | None
    token: str | None
    message: str


# Endpoints


@auth_router.post("/register")
def register(
    req: RegisterRequest,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> RegisterResponse:
    """
    Register a new user account by issuing a QR code URI for the user to scan with their authenticator app.
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


@auth_router.post("/confirm-totp")
def confirm_totp(
    req: ConfirmTOTPRequest,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> dict:
    """
    Confirm the user has scanned the QR code correctly.
    """
    try:
        module.confirm_totp(email=req.email, code=req.code)
        return {"message": "TOTP confirmed successfully. You can now log in."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.get("/totp-setup")
def get_totp_setup(
    email: str,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> RegisterResponse:
    """
    Returns the QR code URI for a user who wants to set up TOTP later.
    """
    try:
        qr_uri = module.get_totp_setup(email=email)
        return RegisterResponse(
            qr_uri=qr_uri, message="Scan this QR code with your authenticator app."
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@auth_router.post("/login")
def login(
    req: LoginRequest,
    response: Response,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> LoginResponse:
    """
    First step of login - verify email and password.
    Returns a challenge token to be used in the verify-otp step.
    """
    try:
        result = module.login(
            email=req.email,
            password=req.password,
        )
        if not result["requires_totp"]:
            response.set_cookie(
                key="access_token",
                value=result["token"],
                httponly=True,
                secure=True,
                samesite="strict",
            )
        return LoginResponse(
            requires_totp=result["requires_totp"],
            challenge_token=result["challenge_token"],
            token=None,
            message="Login successful." if not result["requires_totp"] else "Password verified. Please enter your authenticator code.",
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.post("/verify-otp")
def verify_otp(
    req: VerifyOTPRequest,
    response: Response,
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> dict:
    """
    Second step of login - verify TOTP code.
    Will be issuing a RS256 signed JWT stored in HttpOnly cookie upon success.
    """
    try:
        token = module.verify_otp(
            email=req.email,
            code=req.code,
        )
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=True,
            samesite="strict",
        )
        return {"message": "Login successful."}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.get("/public-key")
def get_public_key(
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> dict:
    """
    Returns the RSA public key for JWT verification
    """
    return {"public_key": module._get_public_key_pem()}
