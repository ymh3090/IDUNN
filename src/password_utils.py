import secrets
from zxcvbn import zxcvbn


def generate_password(length: int = 12, use_symbols: bool = True) -> str:
    """Generate a random password using cryptographically secure randomness.
    Guarantees at least one uppercase, one lowercase, one digit
    (and one symbol if use_symbols is True), then fills the rest randomly
    and shuffles so the guaranteed characters aren't always in the same position."""
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"
    special = "!@#$%^&*()-+_=[]{}|<>?/~"

    password_chars = [
        secrets.choice(upper),
        secrets.choice(lower),
        secrets.choice(digits),
    ]
    if use_symbols:
        password_chars.append(secrets.choice(special))

    all_chars = upper + lower + digits + (special if use_symbols else "")
    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def generate_custom_password(upper_count: int = 0, lower_count: int = 0,
                              digit_count: int = 0, special_count: int = 0) -> str:
    """Generate a password with an exact number of each character type, shuffled.
    At least one count must be greater than 0."""
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"
    special = "!@#$%^&*()-+_=[]{}|<>?/~"

    if upper_count + lower_count + digit_count + special_count == 0:
        raise ValueError("At least one character count must be greater than 0")

    password_chars = []
    password_chars += [secrets.choice(upper) for _ in range(upper_count)]
    password_chars += [secrets.choice(lower) for _ in range(lower_count)]
    password_chars += [secrets.choice(digits) for _ in range(digit_count)]
    password_chars += [secrets.choice(special) for _ in range(special_count)]

    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def check_strength(password: str) -> dict:
    """Returns a strength assessment using zxcvbn's pattern-based analysis
    (dictionary words, sequences, keyboard patterns, l33t speak, repeats)."""
    if len(password) > 72:
        return {
            "score": 4,
            "warning": "",
            "suggestions": [],
            "crack_time": "centuries (password exceeds analysis length, treated as very strong)",
        }
    result = zxcvbn(password)
    return {
        "score": result["score"],
        "warning": result["feedback"]["warning"],
        "suggestions": result["feedback"]["suggestions"],
        "crack_time": result["crack_times_display"]["offline_slow_hashing_1e4_per_second"],
    }

#
# if __name__ == "__main__":
#     test_passwords = [
#         "123",
#         "password",
#         "Password1!",
#         "correct horse battery staple",
#         generate_password(10),
#         generate_custom_password(upper_count=2, lower_count=4, digit_count=2, special_count=2),
#     ]
#     for pw in test_passwords:
#         r = check_strength(pw)
#         print(f"{pw!r} -> score {r['score']}, crack time: {r['crack_time']}")