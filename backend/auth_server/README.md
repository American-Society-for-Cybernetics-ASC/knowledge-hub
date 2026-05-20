# Authentication Server

## Overview
The Authentication Server is a subsystem within the FastAPI backend responsible for user registration, login, session management, and access control. It implements a two-factor authentication flow using Argon2id password hashing and TOTP verification via pyotp.

It is designed as a reusable authentication server for future ASC applications using 
RS256 asymmetric JWT signing.

## Folder Structure
auth/
    __init__.py         - Package initialisation
    models.py           - UserAccount database model and enums
    routes.py           - All authentication endpoints and AuthModule
    jwt_service.py      - JWT issuing, verification and refresh
    totp_service.py     - TOTP secret generation and verification
auth_server_tests/
    - Test files for the authentication server

## Environment Variables
Copy .env.example to .env and fill in the required values:
- RSA_PRIVATE_KEY_PATH: Path to RSA private key file for JWT signing
- FERNET_KEY: Fernet encryption key for TOTP secret storage
- DATABASE_URL: PostgreSQL connection string
- JWT_ISSUER: JWT issuer identifier
- JWT_EXPIRY_MINUTES: Session expiry time in minutes

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register a new user account |
| POST | /auth/login | Validate email and password |
| POST | /auth/verify-otp | Validate TOTP code and issue JWT |
| POST | /auth/logout | Clear JWT cookie |
| POST | /auth/refresh | Refresh JWT token |
| GET | /auth/me | Get current user details |
| GET | /auth/public-key | Get RSA public key for token verification |
| POST | /auth/admin/lock/{user_id} | Lock a user account (Admin only) |
| POST | /auth/admin/unlock/{user_id} | Unlock a user account (Admin only) |

## Security Notes
- Passwords are hashed using Argon2id
- TOTP secrets are encrypted using Fernet before database storage
- JWTs are signed using RS256 asymmetric signing
- RSA private key must be stored outside version control
- JWT tokens are stored in HttpOnly cookies
- Accounts are temporarily locked for 10 minutes after 3 consecutive failed login attempts
- If a further 3 consecutive failed attempts occur after the temporary lockout, the account is permanently locked
- Permanently locked accounts can only be unlocked manually by an administrator via /auth/admin/unlock/{user_id}