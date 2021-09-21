import sqlite3

from os import PathLike
from typing import Callable, Iterator
from dataclasses import dataclass, field
from sqlite3.dbapi2 import OperationalError, ProgrammingError


@dataclass
class Table(object):
    name: str = field(default=None)
    info: list[tuple] = field(default=None)
    json: list[dict[str]] = field(default=None)


class PragmaExtractor(object):
    """
    Extract schema information from sqlite databases using the `pragma
    table_info` directive.
    """

    def get_table_names(self, cursor: sqlite3.Cursor) -> Iterator[Table]:
        """
        Extract the table names from a database connection.
        """

        try:
            cursor.execute("""
                SELECT tbl_name
                FROM sqlite_master
                WHERE type='table';
            """)
        except ProgrammingError as pe:
            raise pe
        except OperationalError as oe:
            raise oe

        tables_raw = cursor.fetchall()
        tables = (Table(table[0]) for table in tables_raw)

        return tables

    def get_col_info(self, cursor: sqlite3.Cursor, table: Table) -> Table:
        """
        Given a Table (with valid name), extract column information in the form
        of a list of tuples, each having the fields of column id, name, data
        type, not null, default value, and private key.
        """

        if table.name is None:
            # INVALID INPUT
            return

        try:
            cursor.execute(f'pragma table_info("{table.name}");')
        except ProgrammingError as pe:
            raise pe
        except OperationalError as oe:
            raise oe

        col_info = cursor.fetchall()
        table.info = col_info

        return table

    def get_col_json(self, table: Table) -> Table:
        """
        Format the information from a Table's info property into JSON and
        populate this into the json field of the Table.
        """

        if table.info is None or table.name is None:
            # INVALID INPUT
            return
        
        def parse_data(col_data: tuple) -> dict[str]:
            _, name, dtype, not_null, default, pk = col_data

            data_json = {
                'column_name': name,
                'data_type': dtype,
                'default_column_data': default,
                'not_null': not_null,
                'primary_key': pk
            }

            return data_json

        col_data = map(parse_data, table.info)

        table_json = {
            'table': table.name,
            'col_data': list(col_data),
        }

        table.json = table_json

        return table

    def get_schema_json(self, cursor: sqlite3.Cursor) -> list[dict[str]]:
        """
        Given a valid database connection, extract the schema as JSON.
        """
        
        tables = self.get_table_names(cursor)

        get_col_data = lambda t: self.get_col_info(cursor, t)
        json_transform = self.get_col_json

        schema_info = map(json_transform, map(get_col_data, tables))

        if schema_info is None:
            # ERROR
            return

        # just build list so result is JSON serializable
        # (as opposed to returning an iterator)
        return [table.json for table in schema_info]

    def get_schema(self, file: PathLike, filter: Callable[[str],str] = None) -> list[dict[str]]:
        """
        Given a file path pointing to a sql file constructing a database,
        extract the corresponding schema encoded as JSON.
        """

        with open(file, 'r') as f:
            data = f.read()

        filtered = data if filter is None else filter(data)

        with sqlite3.connect(':memory:') as conn:

            cur = conn.cursor()

            try:
                cur.executescript(filtered)
            except OperationalError:
                raise OperationalError('Aborted: syntax error in database script')

            return self.get_schema_json(cur)
