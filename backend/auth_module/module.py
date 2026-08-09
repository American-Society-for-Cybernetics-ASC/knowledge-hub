from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone

import pyotp

import database
from database import model
from settings import SETTINGS

ph = PasswordHasher()


class AuthModule:
    def _get_fernet(self) -> Fernet:
        """Returns a Fernet instance using the key from settings"""
        return Fernet(SETTINGS.fernet_key.encode())

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
        session = database.get_session()

        # Check if email already exists
        existing = (
            session.query(model.AuthUser).filter(model.AuthUser.email == email).first()
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

        # Generate QR code URI for authenticator app
        totp = pyotp.TOTP(totp_secret)
        qr_uri = totp.provisioning_uri(name=email, issuer_name="CKH ASC")

        return qr_uri

    def get_totp_setup(self, email: str) -> str:
        """
        Returns the QR code URI for a user to set up TOTP.

        """
        session = database.get_session()

        user = (
            session.query(model.AuthUser).filter(model.AuthUser.email == email).first()
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
        session = database.get_session()

        user = (
            session.query(model.AuthUser).filter(model.AuthUser.email == email).first()
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

    def login(self, email: str, password: str) -> str:
        """
        First step of login - verifies email and password.

        1. Finds user by email
        2. Checks account lock status
        3. Verifies password with Argon2id
        4. Handles failed attempt counting and lockout
        5. Returns a challenge token on success

        Raises ValueError with appropriate message on failure.
        """
        session = database.get_session()

        user = (
            session.query(model.AuthUser).filter(model.AuthUser.email == email).first()
        )

        # Return generic message to prevent user enumeration
        if not user:
            raise ValueError("Invalid email or password")

        # Check permanent admin lock
        if user.admin_locked:
            raise ValueError("Account locked. Please contact an administrator.")

        # Check temporary lockout
        if user.locked_until and user.locked_until > datetime.now():
            raise ValueError("Account temporarily locked. Please try again later.")

        # Verify password
        try:
            ph.verify(user.hash_password, password)
        except VerifyMismatchError:
            # Increment failed attempts
            user.failed_attempt = (user.failed_attempt or 0) + 1

            # After 3 failures - temporary lockout
            if user.failed_attempt >= 3:
                user.locked_until = datetime.now() + timedelta(minutes=10)

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

        # Return challenge token (simple for now - will be proper JWT later)
        return f"challenge:{user.user_id}"

    def verify_otp(self, email: str, code: str) -> dict:
        """
        Second step of login - verifies TOTP code and issues JWT.

        1. Finds user by email
        2. Decrypts stored TOTP secret
        3. Verifies the 6-digit code
        4. Updates last_login timestamp
        5. Returns user info (JWT will be added later)

        Raises ValueError if user not found or code invalid.
        """
        session = database.get_session()

        user = (
            session.query(model.AuthUser).filter(model.AuthUser.email == email).first()
        )

        if not user:
            raise ValueError("User not found")

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

        return {
            "user_id": str(user.user_id),
            "email": user.email,
            "message": "Login successful",
        }
