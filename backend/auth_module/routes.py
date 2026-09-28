from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
import database
from database import model

from utils import BaseModel
from . import AuthModule, user_id, permissions, authorized
from auth_module.model import Permissions, PermissionTier


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
    challenge_token: str


class ConfirmTOTPRequest(BaseModel):
    email: str
    code: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangeEmailRequest(BaseModel):
    new_email: str


class GrantPermissionRequest(BaseModel):
    tier: str


# Response schemas


class RegisterResponse(BaseModel):
    qr_uri: str
    message: str


class LoginResponse(BaseModel):
    challenge_token: str | None
    message: str


class CurrentUserResponse(BaseModel):
    user_id: int
    email: str
    name: str | None
    totp_enabled: bool


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
        if not result["challenge_token"]:
            response.set_cookie(
                key="access_token",
                value=result["token"],
                httponly=True,
                secure=True,
                samesite="strict",
            )
        return LoginResponse(
            challenge_token=result["challenge_token"],
            message="Login successful."
            if not result["challenge_token"]
            else "Password verified. Please enter your authenticator code.",
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
            challenge_token=req.challenge_token,
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


@auth_router.get("/me")
def get_current_user(
    current_user_id: Annotated[int | None, Depends(user_id)],
) -> CurrentUserResponse | None:
    """
    Returns the current authenticated user's details.
    Reads user_id from JWT cookie automatically.
    """
    if current_user_id is None:
        return None

    session = database.get_session()
    user = session.get(model.AuthUser, current_user_id)

    if not user:
        return None

    return CurrentUserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        totp_enabled=user.totp_enabled,
    )


@auth_router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user_id: Annotated[int | None, Depends(user_id)],
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> dict:
    """Change the authenticated user's password."""
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        module.change_password(
            user_id=current_user_id,
            current_password=req.current_password,
            new_password=req.new_password,
        )
        return {"message": "Password updated successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/change-email")
def change_email(
    req: ChangeEmailRequest,
    current_user_id: Annotated[int | None, Depends(user_id)],
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> dict:
    """Change the authenticated user's email address."""
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        module.change_email(
            user_id=current_user_id,
            new_email=req.new_email,
        )
        return {"message": "Email updated successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/disable-totp")
def disable_totp(
    current_user_id: Annotated[int | None, Depends(user_id)],
    module: Annotated[AuthModule, Depends(AuthModule)],
) -> dict:
    """Disable two-factor authentication for the authenticated user."""
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        module.disable_totp(user_id=current_user_id)
        return {"message": "Two-factor authentication disabled."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.get("/users")
def list_users(
    _=Depends(authorized(["auth"], PermissionTier.manager)),
) -> list[dict]:
    """List all users with their permission tiers. Requires manager or above."""
    with database.get_session() as session:
        users = session.query(model.AuthUser).all()
        return [
            {
                "user_id": u.user_id,
                "email": u.email,
                "name": u.name,
                "tier": Permissions.model_validate(u.permissions).tier.value
                if u.permissions and Permissions.model_validate(u.permissions).tier
                else None,
            }
            for u in users
        ]


@auth_router.post("/users/{target_user_id}/permissions")
def grant_permission(
    target_user_id: int,
    req: GrantPermissionRequest,
    current_user_id: Annotated[int | None, Depends(user_id)],
    current_permissions: Annotated[Permissions, Depends(permissions)],
) -> dict:
    """Grant a permission tier to a user."""
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Validate the tier being granted
    try:
        tier = PermissionTier(req.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid permission tier")

    # Permission granting
    if tier == PermissionTier.manager and not current_permissions.includes(["auth"], PermissionTier.adminstrator):
        raise HTTPException(status_code=403, detail="Only administrators can grant manager permissions")
    if tier == PermissionTier.moderator and not current_permissions.includes(["auth"], PermissionTier.manager):
        raise HTTPException(status_code=403, detail="Only managers can grant moderator permissions")
    if tier == PermissionTier.adminstrator:
        raise HTTPException(status_code=403, detail="Cannot grant administrator permissions")

    with database.get_session() as session:
        user = session.get(model.AuthUser, target_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prevent changing permissions of a higher-tier user
        if user.permissions:
            target_perms = Permissions.model_validate(user.permissions)
            if target_perms.tier == PermissionTier.adminstrator:
                raise HTTPException(status_code=403, detail="Cannot modify an administrator's permissions")
            if target_perms.tier == PermissionTier.manager and current_permissions.tier != PermissionTier.adminstrator:
                raise HTTPException(status_code=403, detail="Only administrators can modify a manager's permissions")

        user.permissions = Permissions(tier=tier).model_dump(mode="json")
        session.commit()

    return {"message": f"Permission {req.tier} granted successfully."}