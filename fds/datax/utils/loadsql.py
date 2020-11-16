import os
import pandas as pd
import pyodbc
import re
import sys
from io import StringIO

cwd = os.getcwd()


class IpyExit(SystemExit):
    """Exit Exception for IPython.

    Exception temporarily redirects stderr to buffer.
    """

    def __init__(self):
        sys.stderr = StringIO()

    def __del__(self):
        sys.stderr.close()
        sys.stderr = sys.__stderr__  # restore from backup


def ipy_exit():
    raise IpyExit


def parse_tables_from_query(query_text):
    """
    Validates if the required tables and schema referenced in the SQL Query
    are available via the DNS.
    """

    tables_with_square_brackets_and_quotes = re.findall(
        '(?:from|join)\s+(?:[0-9a-zA-Z\[\]"\_\@\#\$]+\.)?([0-9a-zA-Z\[\]"\_\@\#\$]+\.[0-9a-zA-Z\[\]"\_\@\#\$]+)',
        query_text.lower(),
    )

    tables_referenced = []
    for table in tables_with_square_brackets_and_quotes:
        reference = table.replace("[", "").replace("]", "").replace('"', "")
        tables_referenced.append(reference)

    schema_filter = lambda pair: pair[0] not in [
        "sys",
        "client",
        "fds",
        "fds_scratch",
        "dbo",
        "information_schema",
        "guest",
    ]
    sql_tables = pd.DataFrame(list(filter(schema_filter, tables_referenced)))
    sql_tables = sql_tables.rename(columns={sql_tables.columns[0]: "table"})

    return sql_tables


def get_sql_q(filename, show=1, connection="SDF"):
    """
    Notice: Default behavior references DSN named SDF. If DSN name not SDF, set connection
    argument.

    Parameters
    -----------
    filename: sql script to load
    show: output query text, default show=1
    connection: set to pyodbc connection, default connection='SDF'
    """

    try:
        default_cxn = pyodbc.connect("DSN={d}".format(d=connection))

    except:
        print(
            """Warning: Ensure you have an ODBC connection named SDF with access to the database\n\
where the FactSet Standard DataFeeds reside.\n\nEither create this ODBC connection or update the "loadsql" \
calls with your ODBC name,\nsee docstring for example."""
        )

        ipy_exit()

        # create dataframe containing tables used within SQL query
    with open(os.path.join(cwd, filename), "r", encoding="utf-8-sig") as fd:
        sqlFile = fd.read()
        of_results = parse_tables_from_query(sqlFile)

        # check client's access to tables
        schema_query = """
           SELECT CONCAT(ds.schema_name,'.',ds.table_name) AS 'table_access',
                  CONCAT(mp.feed_schema,'.',mp.table_name) AS 'table_ref',
                  package_name
             FROM ref_v2.ref_metadata_packages AS mp
        LEFT JOIN fds.fds_data_sequences AS ds
               ON ds.schema_name = mp.feed_schema
              AND ds.table_name = mp.table_name
        """
        default_cxn = pyodbc.connect("DSN={d}".format(d=connection))
        tables = pd.read_sql(schema_query, default_cxn)
        default_cxn.close()

        # compare client's access to query tables by merging two togethor
        df = of_results.merge(tables, how="left", left_on="table", right_on="table_ref")

        # check for which tables did not map and store in new list
        nulls = df[df["table_access"] == "."]

    if nulls.empty:
        if show == 1:
            print(sqlFile)
        return sqlFile

    else:
        print(
            """Please contact your FactSet representative for access to the package(s) used in this SQL query.\n\n\
If you currently have access, please download the latest version of the notebook at\nhttps://open.factset.com/"""
        )

        with pd.option_context("display.max_rows", None, "display.max_colwidth", -1):
            display(nulls[["table_ref", "package_name"]])

        ipy_exit()
