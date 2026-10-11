# /// script
# requires-python = ">=3.14"
# dependencies = ["cryptography"]
# ///

from cryptography.hazmat.primitives.asymmetric import rsa;
from cryptography.hazmat.primitives import serialization;
from cryptography.fernet import Fernet;

def main() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    print("Secret key:")
    print(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()).decode())
    print("Fernet key:")
    print(Fernet.generate_key().decode())

if __name__ == "__main__":
    main()
