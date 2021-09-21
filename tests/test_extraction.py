from schematools import Table

def test_table_names(cur, extractor):
    tables = extractor.get_table_names(cur)
    tables = [table.name for table in tables]

    assert tables is not None

    assert set(tables) == {'customers', 'invoices'}

def test_table_info(cur, extractor):
    # tables with no name should be rejected
    assert extractor.get_col_info(cur, Table()) is None

    customer_tbl = Table('customers')
    invoices_tbl = Table('invoices')

    customer_info = extractor.get_col_info(cur, customer_tbl).info
    invoices_info = extractor.get_col_info(cur, invoices_tbl).info

    assert customer_info is not None
    assert invoices_info is not None

    customer_truth = set([
        (0, 'id', 'INTEGER', 0, None, 1),
        (1, 'first_name', 'VARCHAR(40)', 1, None, 0),
        (2, 'last_name', 'VARCHAR(20)', 1, None, 0)
    ])
    invoices_truth = set([
        (0, 'id', 'INTEGER', 0, None, 1),
        (1, 'customer_id', 'INTERGER', 1, None, 0),
        (2, 'total', 'NUMERIC(10,2)', 1, None, 0)
    ])

    assert set(customer_info) == customer_truth
    assert set(invoices_info) == invoices_truth

def test_json_conversion(extractor):
    # tables should be rejected unless they have name and info
    assert extractor.get_col_json(Table()) is None
    assert extractor.get_col_json(Table('test')) is None
    assert extractor.get_col_json(Table(None, list(tuple()))) is None

    customer_tbl = Table('customers')
    invoices_tbl = Table('invoices')

    customer_tbl.info = [
        (0, 'id', 'INTEGER', 0, None, 1),
        (1, 'first_name', 'VARCHAR(40)', 1, None, 0),
        (2, 'last_name', 'VARCHAR(20)', 1, None, 0)
    ]
    invoices_tbl.info = [
        (0, 'id', 'INTEGER', 0, None, 1),
        (1, 'customer_id', 'INTERGER', 1, None, 0),
        (2, 'total', 'NUMERIC(10,2)', 1, None, 0)
    ]

    customer_json_tbl = extractor.get_col_json(customer_tbl)
    customer_target_repr = "{'table': 'customers', 'col_data': [{'column_name': 'id', 'data_type': 'INTEGER', 'default_column_data': None, 'not_null': 0, 'primary_key': 1}, {'column_name': 'first_name', 'data_type': 'VARCHAR(40)', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}, {'column_name': 'last_name', 'data_type': 'VARCHAR(20)', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}]}"

    invoices_json_tbl = extractor.get_col_json(invoices_tbl)
    invoices_target_repr = "{'table': 'invoices', 'col_data': [{'column_name': 'id', 'data_type': 'INTEGER', 'default_column_data': None, 'not_null': 0, 'primary_key': 1}, {'column_name': 'customer_id', 'data_type': 'INTERGER', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}, {'column_name': 'total', 'data_type': 'NUMERIC(10,2)', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}]}"

    assert customer_json_tbl is not None
    assert invoices_json_tbl is not None

    assert customer_json_tbl.json.__repr__() == customer_target_repr
    assert invoices_json_tbl.json.__repr__() == invoices_target_repr

def test_schema_json(cur, extractor):
    target_json = [
        "{'table': 'customers', 'col_data': [{'column_name': 'id', 'data_type': 'INTEGER', 'default_column_data': None, 'not_null': 0, 'primary_key': 1}, {'column_name': 'first_name', 'data_type': 'VARCHAR(40)', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}, {'column_name': 'last_name', 'data_type': 'VARCHAR(20)', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}]}",
        "{'table': 'invoices', 'col_data': [{'column_name': 'id', 'data_type': 'INTEGER', 'default_column_data': None, 'not_null': 0, 'primary_key': 1}, {'column_name': 'customer_id', 'data_type': 'INTERGER', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}, {'column_name': 'total', 'data_type': 'NUMERIC(10,2)', 'default_column_data': None, 'not_null': 1, 'primary_key': 0}]}",
    ]

    schema_json = extractor.get_schema_json(cur)

    schema_json = [json.__repr__() for json in schema_json]

    assert schema_json.__repr__() == target_json.__repr__()
