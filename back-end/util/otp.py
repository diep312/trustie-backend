import random

def generate_otp(length=6) -> str:
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])