import sqlite3
from os import path
from sqlite3 import Error


"""Handles the connection with the database 
    and query execution"""


class Database:
    def __init__(self, logger):
        ROOT = path.dirname(path.realpath(__file__))
        self._db_file = path.join(ROOT, "RegisteredUser.db")
        self._logger = logger
        self._conn = None
        self._connect()

    def _connect(self) -> None:
        try:
            self._conn = sqlite3.connect(self._db_file)
        except Error as e:
            self._logger.info(str(e))

    def fetch_from_db(self) -> any:
        query = 'select * from registered'
        cursor = self._conn.cursor()
        cursor.execute(query)

        result = cursor.fetchall()
        return result

    def post_to_db(self, query: str) -> str:
        query = "insert into registered(firstName, lastName, address1, address2, city, " \
                "state, zip, country, dateRegistered) " + query
        with self._conn:
            cursor = self._conn.cursor()
            try:
                cursor.execute(query)
                print(cursor.lastrowid)
                return 'Success'
            except Exception as e:
                return str(e)

