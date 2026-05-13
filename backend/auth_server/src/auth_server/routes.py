from models import LoginRequest, RegistrationRequest


class AuthModule:
    """
    Main authentication module that handles all auth endpoints.
    Implements the IModule interface.
    Manages registration, login, TOTP verification and JWT issuing.
    """

    def register(self, req: RegistrationRequest):
        """
        POST /auth/register
        Creates a new user account.
        Hashes password with Argon2id.
        Generates TOTP secret and returns QR code to frontend.
        """
        pass

    def confirm_totp(self, code: str) -> bool:
        """
        Called after registration to confirm user scanned QR code.
        Verifies the 6 digit code from authenticator app.
        Sets totp_enabled to True on success.
        Returns True if confirmed, False if not.
        """
        pass

    def login(self, req: LoginRequest):
        """
        POST /auth/login
        Validates email and pasSsword.
        Checks account lock status and member status.
        Issues a short lived challenge token on success.
        """
        pass

    def verify_otp(self, code: str):
        """
        POST /auth/verify-otp
        Validates the 6 digit TOTP code.
        Issues a full JWT stored in HttpOnly cookie on success.
        """
        pass

    def logout(self):
        """
        POST /auth/logout
        Clears the HttpOnly JWT cookie.
        Ends the user session.
        """
        pass

    def refresh(self):
        """
        POST /auth/refresh
        Issues a new JWT if current token is valid.
        Extends the session expiry time.
        """
        pass

    def get_me(self):
        """
        GET /auth/me
        Returns the authenticated user's identity and role
        from the JWT claims.
        """
        pass

    def admin_lock(self, user_id: str):
        """
        POST /auth/admin/lock/{user_id}
        Permanently locks a user account.
        Administrators only.
        """
        pass

    def admin_unlock(self, user_id: str):
        """
        POST /auth/admin/unlock/{user_id}
        Unlocks a permanently locked user account.
        Administrators only.
        """
        pass

    def get_public_key(self):
        """
        GET /auth/public-key
        Returns the RSA public key.
        Used by future ASC applications to verify JWT tokens
        without needing the private key.
        """
        pass

    def verify_token(self, token: str):
        """
        Verifies a JWT token on every protected request.
        Checks signature using RSA public key.
        Checks token expiry.
        Returns TokenPayload if valid.
        Raises 401 if invalid or expired.
        """
        pass