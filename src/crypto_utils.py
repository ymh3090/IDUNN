# import hashlib
# import base64
# import os
# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
# from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
# salt = os.urandom(16)
# kdf = Argon2id(
#     salt=salt,length=32,iterations=1,lanes=4,memory_cost=64 * 1024,ad=None,secret=None,
# )
#
# key = kdf.derive(b"my great password")
# # verify
# kdf = Argon2id(
#     salt=salt,
#     length=32,
#     iterations=1,
#     lanes=4,
#     memory_cost=64 * 1024,
#     ad=None,
#     secret=None,
# )
# kdf.verify(b"my great password", key)
#
#
# # day 1
# # 1. Take a password (string) + a salt (bytes) as input
# # 2. Feed both into Argon2id
# # 3. Get back 32 raw bytes
# # 4. Return those bytes
# #
# #
# # def derive_key(password: str, salt: bytes) -> bytes:
# #     kdf = Argon2id(salt=salt, length=32, iterations=1, lanes=4, memory_cost=64*1024)
# #     return kdf.derive(password.encode())
# Implementation
# Fernet is built on top of a number of standard cryptographic primitives. Specifically it uses:
#
# AES in CBC mode with a 128-bit key for encryption; using PKCS7 padding.
#
# HMAC using SHA256 for authentication.
#
# Initialization vectors are generated using os.urandom().









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
        iterations=1,
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

if __name__ == "__main__":
    salt = generate_salt()
    key1 = derive_key("test123", salt)
    key2 = derive_key("test123", salt)
    key3 = derive_key("different_pw", salt)

    encrypted=encrypt("bypass0rd",key1)
    decrypted = decrypt(encrypted,key2)
    print("decryption of the encrypted password is: ",decrypted)




    print("same password, same salt -> same key:", key1 == key2)
    print("different password -> different key:", key1 != key3)