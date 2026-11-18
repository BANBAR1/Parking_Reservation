from parking_reservation.config import database_url


def test_database_url_uses_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/test")
    assert database_url() == "postgresql://example/test"


def test_database_url_uses_compose_default(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert database_url() == ("postgresql://roman:iamdamngood@localhost:5432/parking")
