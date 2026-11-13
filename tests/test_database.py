def test_database_answers(connection):
    assert connection.execute("SELECT 1").fetchone() == (1,)
