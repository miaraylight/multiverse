import sqlite3


class DatabaseException(Exception):
    pass


def create_select_statement(table_name: str, fields: list[str] = None) -> str:
    """
    Create SELECT-statement from field list

    :param table_name: Name of the table
    :param fields: List of the fields names

    :return: SELECT-clause
    """
    query = 'SELECT '
    if fields is None:
        query += "*"
    else:
        for idx, field in enumerate(fields):
            if idx == 0:
                query += f'"{field}"'
            else:
                query += f', "{field}"'

    query += f' FROM {table_name} '

    return query


def create_where_statement(where: dict[str, str]) -> str:
    """
    Create WHERE-statement from dictionary

    :param where: Dictionary with WHERE-parameters

    :return: WHERE-clause
    """
    query = 'WHERE '
    for idx, param in enumerate(where.keys()):
        value = where[param]

        if idx == 0:
            query += f'"{param}" = "{value}"'
        else:
            query += f' AND "{param}" = "{value}"'

    return query


class SQLite:
    """
    Class to working with SQLite databases
    """
    def __init__(self, db_file: str):
        """
        Initialize SQLite

        :param db_file: Full path to the SQLite .db file
        """
        self.__conn = None
        self.__cursor = None
        self.__db_file = db_file

    def open(self) -> None:
        """
        Open database
        """
        try:
            self.__conn = sqlite3.connect(self.__db_file)
            self.__cursor = self.__conn.cursor()
        except Exception as e:
            raise DatabaseException(f'SQLite connection error: {e}')

    def close(self) -> None:
        """
        Close database
        """
        if self.__conn is not None:
            self.__conn.close()

    def __enter__(self):
        """
        Open database
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close database
        """
        self.close()

    def select(self, table_name: str, fields: list[str] = None, where: dict[str, str] = None,
               orderby: str = None, groupby: str = None) -> list:
        """
        Select records from table

        :param table_name: Name of the table
        :param fields: Field list to select (empty for all)
        :param where: Dictionary with WHERE parameters
        :param orderby: Field name to order records
        :param groupby: Field name to group records
        :return:
        """
        if self.__conn is None or self.__cursor is None:
            raise DatabaseException('No opened database')

        try:
            result = []

            if fields is None:
                self.__cursor.execute(f'PRAGMA table_info("{table_name}")')
                fields = [entry[1] for entry in self.__cursor.fetchall()]

            query = create_select_statement(table_name, fields)

            if where is not None:
                query += create_where_statement(where)

            if orderby is not None:
                query += f' ORDER BY {orderby}'

            if groupby is not None:
                query += f' GROUP BY {groupby}'

            self.__cursor.execute(query)
            db_result = self.__cursor.fetchall()

            for db_entry in db_result:
                entry = {}
                for idx, field in enumerate(fields):
                    entry[field] = db_entry[idx]

                result.append(entry)

            return result
        except Exception as e:
            raise DatabaseException(f'SQLite error: {e}')

    def insert(self, table_name: str, values: dict[str, str]) -> int:
        """
        Insert values into table

        :param table_name: Name of the table
        :param values: Dictionary with values to insert
        """
        if self.__conn is None or self.__cursor is None:
            raise DatabaseException('No opened database')

        try:
            query = f'INSERT INTO {table_name}('
            insert_values = ''
            for idx, param in enumerate(values.keys()):
                value = values[param]
                if idx == 0:
                    query += f'"{param}"'
                    insert_values += f'"{value}"'
                else:
                    query += f', "{param}"'
                    insert_values += f', "{value}"'

            query += f') VALUES ({insert_values})'

            self.__cursor.execute(query)
            self.__conn.commit()

            return self.__cursor.lastrowid
        except Exception as e:
            raise DatabaseException(f'SQLite error: {e}')

    def update(self, table_name: str, values: dict[str, str], where: dict[str, str] = None) -> None:
        """
        Update table from a dictionary values

        :param table_name: Name of the table
        :param values: Dictionary with values to update
        :param where: Dictionary with WHERE parameters
        """
        if self.__conn is None or self.__cursor is None:
            raise DatabaseException('No opened database')

        try:
            query = f'UPDATE "{table_name}" SET '

            for idx, param in enumerate(values.keys()):
                value = values[param]
                if idx == 0:
                    query += f'"{param}" = "{value}"'
                else:
                    query += f', "{param}" = "{value}"'

            if where is not None:
                query += ' ' + create_where_statement(where)

            self.__cursor.executescript(query)
        except Exception as e:
            raise DatabaseException(f'SQLite error: {e}')

    def delete(self, table_name: str, where: dict[str, str] = None) -> None:
        """
        Delete record(s) from table

        :param table_name: Name of the table
        :param where: Dictionary with WHERE parameters
        """
        if self.__conn is None or self.__cursor is None:
            raise DatabaseException('No opened database')

        try:
            query = f'DELETE FROM "{table_name}" '

            if where is not None:
                query += create_where_statement(where)

            self.__cursor.executescript(query)
        except Exception as e:
            raise DatabaseException(f'SQLite error: {e}')

    def custom_select(self, query: str, commit: bool = False) -> None:
        """
        Perform custom SELECT-request

        :param query: SQL query
        :param commit: True to run SQL COMMIT-command
        """
        if self.__conn is None or self.__cursor is None:
            raise DatabaseException('No opened database')

        try:
            self.__cursor.executescript(query)
            if commit:
                self.__conn.commit()
        except Exception as e:
            raise DatabaseException(f'SQLite error: {e}')
