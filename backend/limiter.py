import os

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

LOGIN_RATE = os.getenv("RATE_LIMIT_LOGIN", "10/minute")
REGISTER_RATE = os.getenv("RATE_LIMIT_REGISTER", "5/minute")
