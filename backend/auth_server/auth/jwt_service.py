from datetime import datetime


class TokenPayload:
    """
    Represents the decoded contents of a JWT token.
    Contains user identity and role information.
    """

    sub: str  # User UUID
    email: str  # User email
    roles: dict  # Dictionary of module specific roles
    exp: datetime  # Token expiry time
    iss: str  # Issuer - ckh.asc-cybernetics.org


class JWTService:
    """
    Handles all JWT operations including issuing,
    verifying and refreshing tokens using RS256 signing.
    """

    def issue(self, user) -> str:
        """
        Issues a signed JWT token for a given user.
        Signs using RSA private key (RS256).
        Returns the token as a string.
        """
        pass

    def verify(self, token: str) -> TokenPayload:
        """
        Verifies a JWT token signature and expiry.
        Returns the decoded TokenPayload if valid.
        Raises an error if invalid or expired.
        """
        pass

    def refresh(self, token: str) -> str:
        """
        Issues a new JWT token if the current token is valid.
        Extends the session expiry time.
        Returns the new token as a string.
        """
        pass

    def get_public_key(self):
        """
        Returns the RSA public key.
        Used by other ASC applications to verify tokens
        without needing the private key.
        """
        pass
