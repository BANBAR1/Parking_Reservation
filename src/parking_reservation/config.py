import os

DEFAULT_DATABASE_URL = "postgresql://roman:iamdamngood@localhost:5432/parking"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
