import logging
from functools import lru_cache
from logging import Logger
from typing import Union

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


@lru_cache
def get_logger(name: Union[str, None] = "app_logger") -> Logger:
    logger = logging.getLogger(name if name else __name__)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class Settings(BaseSettings):
    authjwt_secret_key: str
    jwt_secret: str
    jwt_expire_time: int
    reset_password_token_secret: str
    verification_token_secret: str
    db_url: str
    # jwt_expire_time: int
    # algorithm: str
    # google_client_id: str
    # google_client_secret: str
    # sqlite_path: str
    # paystack_public_key: str
    # sender_name: str = Field(default="Spirit Zone")
    # sender_email: str = Field(default="kyei9189@gmail.com")

    # paystack_secret_key: str
    # brevo_api_key: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
