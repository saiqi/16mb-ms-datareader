import pytest
import pymonetdb

from nameko.testing.services import worker_factory
import bson.json_util

from application.services.datareader import DatareaderService


@pytest.fixture
def connection(host, user, password, database, port):
    _conn = pymonetdb.connect(username=user, hostname=host, password=password, database=database, port=port)

    yield _conn

    def clean_tables():
        cursor = _conn.cursor()

        cursor.execute('SELECT NAME FROM SYS.TABLES WHERE SYSTEM=0')

        has_cleaned = False

        for table in cursor.fetchall():
            has_cleaned = True
            _conn.execute('DROP TABLE {table}'.format(table=table[0]))
        return has_cleaned

    max_retry = 2
    has_cleaned = True
    tries = 0

    while tries < max_retry and has_cleaned:
        has_cleaned = clean_tables()
        tries += 1

    _conn.close()


def test_select(connection):
    connection.execute('CREATE TABLE T_TEST AS SELECT 1 AS ID UNION ALL SELECT 2 AS ID')

    service = worker_factory(DatareaderService, connection=connection)
    res = bson.json_util.loads(service.select('SELECT * FROM T_TEST ORDER BY ID'))

    assert len(res) == 2
    assert 'id' in res[0]
    assert res[0]['id'] == 1

    res = bson.json_util.loads(service.select('SELECT * FROM T_TEST WHERE ID = %s', [1]))

    assert len(res) == 1
    assert 'id' in res[0]
    assert res[0]['id'] == 1

    res = bson.json_util.loads(service.select('SELECT * FROM T_TEST WHERE ID = %s', [1], fetchone=True))

    assert type(res) == dict
    assert 'id' in res
    assert res['id'] == 1

    res = bson.json_util.loads(service.select('SELECT * FROM T_TEST', limit=1))

    assert len(res) == 1
