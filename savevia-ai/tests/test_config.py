import os
from unittest.mock import patch

import pytest


def test_settings_loads_from_env():
    from app.core.config import Settings

    with patch.dict(
        os.environ,
        {
            "DB_HOST": "db.example.com",
            "DB_PORT": "3307",
            "DB_NAME": "mydb",
            "DB_USER": "u",
            "DB_PASSWORD": "p",
            "REDIS_HOST": "redis.example.com",
            "REDIS_PORT": "6380",
            "JWT_SECRET": "secret-at-least-32-chars-long-xxxxxx",
            "USER_SERVICE_URL": "http://user:8081",
            "CARD_SERVICE_URL": "http://card:8082",
            "OPENAI_API_KEY": "sk-test",
        },
        clear=True,
    ):
        s = Settings(_env_file=None)
        assert s.db_host == "db.example.com"
        assert s.db_port == 3307
        assert s.db_url.startswith("mysql+aiomysql://u:p@db.example.com:3307/mydb")
        assert s.redis_url == "redis://redis.example.com:6380/0"
        assert s.jwt_secret == "secret-at-least-32-chars-long-xxxxxx"
        assert s.user_service_url == "http://user:8081"
        assert s.card_service_url == "http://card:8082"
        assert s.openai_api_key == "sk-test"


def test_settings_rejects_short_jwt_secret():
    from app.core.config import Settings
    from pydantic import ValidationError

    with patch.dict(
        os.environ,
        {
            "DB_HOST": "x", "DB_PORT": "3306", "DB_NAME": "x", "DB_USER": "x",
            "DB_PASSWORD": "x", "REDIS_HOST": "x", "REDIS_PORT": "6379",
            "JWT_SECRET": "too-short",
            "USER_SERVICE_URL": "http://x", "CARD_SERVICE_URL": "http://x",
        },
        clear=True,
    ):
        with pytest.raises(ValidationError):
            Settings(_env_file=None)


def test_openai_api_key_optional():
    from app.core.config import Settings

    with patch.dict(
        os.environ,
        {
            "DB_HOST": "db.example.com",
            "DB_PORT": "3306",
            "DB_NAME": "mydb",
            "DB_USER": "u",
            "DB_PASSWORD": "p",
            "REDIS_HOST": "redis.example.com",
            "REDIS_PORT": "6379",
            "JWT_SECRET": "secret-at-least-32-chars-long-xxxxxx",
            "USER_SERVICE_URL": "http://user:8081",
            "CARD_SERVICE_URL": "http://card:8082",
        },
        clear=True,
    ):
        s = Settings(_env_file=None)
        assert s.openai_api_key == ""


def test_password_with_special_chars_is_url_encoded():
    from app.core.config import Settings

    with patch.dict(
        os.environ,
        {
            "DB_HOST": "db.example.com",
            "DB_PORT": "3306",
            "DB_NAME": "mydb",
            "DB_USER": "u",
            "DB_PASSWORD": "p@ss:word/123",
            "REDIS_HOST": "redis.example.com",
            "REDIS_PORT": "6379",
            "JWT_SECRET": "secret-at-least-32-chars-long-xxxxxx",
            "USER_SERVICE_URL": "http://user:8081",
            "CARD_SERVICE_URL": "http://card:8082",
        },
        clear=True,
    ):
        s = Settings(_env_file=None)
        assert "p%40ss%3Aword%2F123" in s.db_url
