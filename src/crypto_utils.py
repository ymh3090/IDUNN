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
    return kdf.derive(password.encode())


if __name__ == "__main__":
    salt = generate_salt()
    key1 = derive_key("test123", salt)
    key2 = derive_key("test123", salt)
    key3 = derive_key("different_pw", salt)

    print("same password, same salt -> same key:", key1 == key2)
    print("different password -> different key:", key1 != key3)