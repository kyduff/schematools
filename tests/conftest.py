import sqlite3
from sqlite3.dbapi2 import OperationalError
import pytest

from schematools import PragmaExtractor

@pytest.fixture
def con():
    connection = sqlite3.connect(':memory:')
    yield connection
    connection.close()

@pytest.fixture
def cur(con):
    cursor = con.cursor()

    setup_script = ("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name VARCHAR(40) NOT NULL,
            last_name VARCHAR(20) NOT NULL
        );

        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            customer_id INTERGER NOT NULL,
            total NUMERIC(10,2) NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        );
    """)

    cursor.executescript(setup_script)
    yield cursor

    try:
        cursor.close()
    except OperationalError:
        pass

@pytest.fixture
def extractor():
    return PragmaExtractor()