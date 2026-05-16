from fastapi import FastAPI
from shared.singleton import register_singleton
from auth.routes import auth_router
from auth.totp_service import TOTPService
from auth.jwt_service import JWTService

register_singleton(TOTPService, TOTPService())
register_singleton(TOTPService, JWTService())

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
