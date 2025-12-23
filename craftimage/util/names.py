import string


def random_name(prefix: str, suffix: str, rng) -> str:
    chars = string.ascii_lowercase + string.digits
    token = "".join(rng.choice(chars) for _ in range(6))
    return f"{prefix}_{token}{suffix}"
