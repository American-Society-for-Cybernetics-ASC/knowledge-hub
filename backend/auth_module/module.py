from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone
from jose import jwt
from cryptography.hazmat.primitives import serialization

import pyotp

from audit_log.module import AuditLogModule
from database.types import AuditPermissionCategory
import database
from database import model
from settings import SETTINGS

ph = PasswordHasher()


class AuthModule:
    def _get_fernet(self) -> Fernet:
        """Returns a Fernet instance using the key from settings"""
        return Fernet(SETTINGS.fernet_key.encode())

    def _get_private_key(self):
        """Loads the RSA private key from settings for JWT signing"""
        key_data = SETTINGS.secret_key.strip()

        # Add PEM framing if not present during testing
        if not key_data.startswith("-----"):
            key_data = f"-----BEGIN RSA PRIVATE KEY-----\n{key_data}\n-----END RSA PRIVATE KEY-----"

        return serialization.load_pem_private_key(key_data.encode(), password=None)

    def _get_public_key_pem(self) -> str:
        private_key = self._get_private_key()
        public_key = private_key.public_key()
        return public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def register(self, email: str, password: str, display_name: str) -> str:
        """
        Registers a new user account.

        1. Checks email is not already taken
        2. Hashes password with Argon2id
        3. Generates unique TOTP secret
        4. Encrypts TOTP secret with Fernet
        5. Saves user to database
        6. Returns QR code URI for authenticator app

        Raises ValueError if email already exists.
        """
        with database.get_session() as session:
            # Check if email already exists
            existing = (
                session.query(model.AuthUser)
                .filter(model.AuthUser.email == email)
                .first()
            )

            if existing:
                raise ValueError("Email already registered")

            # Hash the password using Argon2id
            hashed_password = ph.hash(password)

            # Generate unique TOTP secret
            totp_secret = pyotp.random_base32()

            # Encrypt TOTP secret before storing
            f = self._get_fernet()
            encrypted_secret = f.encrypt(totp_secret.encode()).decode()

            # Create new user
            new_user = model.AuthUser(
                email=email,
                hash_password=hashed_password,
                totp_secret=encrypted_secret,
                totp_enabled=False,
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            AuditLogModule().post_audit(
                AuditPermissionCategory.auth, f"An account was registered for {email}"
            )

            # Generate QR code URI for authenticator app
            totp = pyotp.TOTP(totp_secret)
            qr_uri = totp.provisioning_uri(name=email, issuer_name="CKH ASC")

            return qr_uri

    def get_totp_setup(self, email: str) -> str:
        """
        Returns the QR code URI for a user to set up TOTP.

        """
        with database.get_session() as session:
            user = (
                session.query(model.AuthUser)
                .filter(model.AuthUser.email == email)
                .first()
            )

        if not user:
            raise ValueError("User not found")

        # Decrypt TOTP secret
        f = self._get_fernet()
        decrypted_secret = f.decrypt(user.totp_secret.encode()).decode()

        # Generate QR code URI
        totp = pyotp.TOTP(decrypted_secret)
        qr_uri = totp.provisioning_uri(name=email, issuer_name="CKH ASC")

        return qr_uri

    def confirm_totp(self, email: str, code: str) -> bool:
        """
        Confirms the user has scanned the QR code correctly.
        Verifies the 6-digit code and sets totp_enabled to True.

        Raises ValueError if user not found or code is invalid.
        """
        with database.get_session() as session:
            user = (
                session.query(model.AuthUser)
                .filter(model.AuthUser.email == email)
                .first()
            )

            if not user:
                raise ValueError("User not found")

            # Decrypt TOTP secret
            f = self._get_fernet()
            decrypted_secret = f.decrypt(user.totp_secret.encode()).decode()

            # Verify the code
            totp = pyotp.TOTP(decrypted_secret)
            if not totp.verify(code):
                raise ValueError("Invalid TOTP code")

            # Mark TOTP as enabled
            user.totp_enabled = True
            session.commit()

            return True

    def login(self, email: str, password: str) -> dict:
        """
        First step of login - verifies email and password.

        1. Finds user by email
        2. Checks account lock status
        3. Verifies password with Argon2id
        4. Handles failed attempt counting and lockout
        5. Returns a challenge token on success

        Raises ValueError with appropriate message on failure.
        """
        with database.get_session() as session:
            user = (
                session.query(model.AuthUser)
                .filter(model.AuthUser.email == email)
                .first()
            )

            # Return generic message to prevent user enumeration
            if not user:
                raise ValueError("Invalid email or password")

            # Check permanent admin lock
            if user.admin_locked:
                raise ValueError("Account locked. Please contact an administrator.")

            # Check temporary lockout
            if user.locked_until and user.locked_until > datetime.now(timezone.utc):
                raise ValueError("Account temporarily locked. Please try again later.")

            # Verify password
            try:
                ph.verify(user.hash_password, password)
            except VerifyMismatchError:
                # Increment failed attempts
                user.failed_attempt = (user.failed_attempt or 0) + 1

                # After 3 failures - temporary lockout
                if user.failed_attempt >= 3:
                    user.locked_until = datetime.now(timezone.utc) + timedelta(
                        minutes=10
                    )

                # After 6 total failures - permanent lock
                if user.failed_attempt >= 6:
                    user.admin_locked = True
                    user.locked_until = None

                session.commit()
                raise ValueError("Invalid email or password")

            # Password correct - reset failed attempts
            user.failed_attempt = 0
            user.locked_until = None
            session.commit()

            # JWT issual if user has not enabled TOTP
            if not user.totp_enabled:
                payload = {
                    "sub": str(user.user_id),
                    "email": user.email,
                    "iss": SETTINGS.jwt_issuer,
                    "exp": datetime.now(timezone.utc)
                    + timedelta(minutes=SETTINGS.jwt_expiry_minutes),
                }
                token = jwt.encode(payload, self._get_private_key(), algorithm="RS256")
                return {"challenge_token": None, "token": token}
            # Return challenge token
            return {"challenge_token": f"challenge:{user.user_id}", "token": None}

    def verify_otp(self, email: str, code: str, challenge_token: str) -> str:
        """
        Second step of login - verifies TOTP code and issues JWT.

        1. Finds user by email
        2. Decrypts stored TOTP secret
        3. Verifies the 6-digit code
        4. Updates last_login timestamp
        5. Issue JWT Token

        Raises ValueError if user not found or code invalid.
        """
        with database.get_session() as session:
            user = (
                session.query(model.AuthUser)
                .filter(model.AuthUser.email == email)
                .first()
            )

            if not user:
                raise ValueError("User not found")

            # Validate the challenge token
            expected_token = f"challenge:{user.user_id}"
            if challenge_token != expected_token:
                raise ValueError("Invalid challenge token")

            # Decrypt TOTP secret
            f = self._get_fernet()
            decrypted_secret = f.decrypt(user.totp_secret.encode()).decode()

            # Verify TOTP code
            totp = pyotp.TOTP(decrypted_secret)
            if not totp.verify(code):
                raise ValueError("Invalid TOTP code")

            # Update last login
            user.last_login = datetime.now(timezone.utc)
            session.commit()

            # JWT payload
            payload = {
                "sub": str(user.user_id),
                "email": user.email,
                "iss": SETTINGS.jwt_issuer,
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=SETTINGS.jwt_expiry_minutes),
            }

            # Sign the JWT with RSA private key
            token = jwt.encode(payload, self._get_private_key(), algorithm="RS256")

            return token

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """
        Changes the user's password.

        1. Find user by user_id
        2. Verifies current password
        3. Hashes and saves new password
        """

        with database.get_session() as session:
            user = session.get(model.AuthUser, user_id)

            if not user or not user.hash_password:
                raise ValueError("User not found")

            try:
                ph.verify(user.hash_password, current_password)
            except VerifyMismatchError:
                raise ValueError("Current password is incorrect")

            user.hash_password = ph.hash(new_password)
            session.commit()

    def change_email(self, user_id: int, new_email: str) -> None:
        """
        Changes the user's email address.

        1. Checks new email is not already taken
        2. Updates the email
        """

        with database.get_session() as session:
            existing = (
                session.query(model.AuthUser)
                .filter(model.AuthUser.email == new_email)
                .first()
            )

            if existing:
                raise ValueError("Email already in use")

            user = session.get(model.AuthUser, user_id)
            if not user:
                raise ValueError("User not found")

            user.email = new_email
            session.commit()

    def disable_totp(self, user_id: int) -> None:
        """
        Disables two-factor authentication for the user.
        """
        with database.get_session() as session:
            user = session.get(model.AuthUser, user_id)

            if not user:
                raise ValueError("User not found")

            user.totp_enabled = False
            session.commit()