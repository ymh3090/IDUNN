import base64
import datetime
from cryptography.fernet import Fernet
import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

def generate_salt() -> bytes:
    return os.urandom(16)


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=2,
        lanes=4,
        memory_cost=64 * 1024,
    )
    rawkey = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(rawkey)   # <- new line, makes it Fernet-compatible

def encrypt(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt(token: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token).decode()

# if __name__ == "__main__":
#     salt = generate_salt()
#     key1 = derive_key("test123", salt)
#     key2 = derive_key("test123", salt)
#     key3 = derive_key("different_pw", salt)
#
#     encrypted=encrypt("bypass0rd",key1)
#     decrypted = decrypt(encrypted,key2)
#     print("decryption of the encrypted password is: ",decrypted)
#
#
#     print("same password, same salt -> same key:", key1 == key2)
#     print("different password -> different key:", key1 != key3)