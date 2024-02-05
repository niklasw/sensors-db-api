#!/usr/bin/env python3

import sqlite3
import sqlite3
from datetime import datetime
from sqlite3 import Error
from pathlib import Path


class sqlite_db:

    def __init__(self, db_file, max_rows=5):
        self.file = Path(db_file)
        self.directory = self.file.parent
        self.connection = None
        self.max_rows = max_rows
        if not self.directory.is_dir():
            try:
                self.directory.mkdir()
            except Exception as e:
                print(f'Failed to create db directory {self.directory}')

    def connect(self):
        """ create a database connection to a SQLite database """
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.file, check_same_thread=False)
            except Error as e:
                print(e)
                print(f'Failed to connect to database {self.file}')
                return False
            print(self.connection)
        return True

    def get_tables(self):
        if self.connect():
            cursor = self.connection.cursor()
            cursor.execute('''SELECT name FROM sqlite_master
                              WHERE type="table";''')
            tables = cursor.fetchall()
                # Iterate over each table and get its columns
            table_columns = {}
            for table in tables:
                table_name = table[0]
                cursor.execute("PRAGMA table_info({});".format(table_name))
                columns = cursor.fetchall()
                column_names = [column[1] for column in columns]
                table_columns[table_name] = column_names
            return table_columns
        return []

    def get_measurement_names(self, table_name):
        if self.connect():
            cursor = self.connection.cursor()
            cursor.execute(f'SELECT DISTINCT name FROM {table_name};')
            return cursor.fetchall()
        return []

    def create_table(self, table_name):
        if self.connect():
            cursor = self.connection.cursor()
            try:
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        time REAL NOT NULL,
                        value REAL
                    )'''
                )
            except Exception as e:
                print(e)
                print(f'create_table {table_name} failed', flush=True)
                return False

            try:
                cursor.execute(f'''
                    CREATE TRIGGER IF NOT EXISTS enforce_max_rows
                    AFTER INSERT ON {table_name}
                    BEGIN
                        -- Delete rows from the top if the maximum limit is exceeded
                        DELETE FROM {table_name}
                        WHERE id IN (
                            SELECT id
                            FROM {table_name}
                            ORDER BY id DESC
                            LIMIT -1 OFFSET {self.max_rows}
                        );
                    END
                ''')
            except Exception as e:
                print(e)
                print('Table max_row limit trigger failed', flush=True)
                return False
            return True

    def insert(self, table_name, column, value):
        if self.create_table(table_name):
            time = datetime.now().timestamp()
            cursor = self.connection.cursor()
            cursor.execute(f'''
                INSERT INTO {table_name} (name, time, value) VALUES (?, ?, ?)
                ''', (column, time, value)
            )
            self.connection.commit()

    def select_all(self, table_name):
        if self.connect():
            cursor = self.connection.cursor()
            cursor.execute(f'SELECT * FROM {table_name}')
            for item in cursor.fetchall():
                print(item)

    def get_transient_data(self, table_name, column, from_time=0):
        result = []
        if self.connect():
            cursor=self.connection.cursor()
            query = f'SELECT time,value from {table_name} WHERE name IS "{column}"'
            try:
                if from_time < 0:
                    query += f' ORDER BY rowid DESC LIMIT {abs(from_time)}'
                else:
                    query += f' AND time > {from_time}'
                cursor.execute(query)
                result = cursor.fetchall()
            except Exception as e:
                print(e)
                print('get_transient_data failed')

        return result


    def close(self):
        self.connection.close()


if __name__ == '__main__':

    DB = sqlite_db('./db/database.sqlite')
    DB.insert('niklas',
              'sensors/temperature/1',
               datetime.now().second)
    result = DB.get_transient_data('niklas', 'sensors/temperature/1', 0)
    for item in result:
        print(item)
    DB.close()
