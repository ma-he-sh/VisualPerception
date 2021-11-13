import sqlite3
from datetime import datetime

class DB():
    def __init__(self):
        self.conn = self.get_conn()

    def get_conn(self):
        self.conn = sqlite3.connect( "database.db" )
        self.row_factory = sqlite3.Row
        return self.conn

    def set( self, query ):
        self.conn.execute( query )
        self.commit()
        self.conn.close()

    def get( self, query ):
        data = self.conn.execute( query )
        self.conn.close()
        if data is None:
            return False
        return data

    def close(self):
        self.conn.close()

    def get_db_connection(self):
        conn = sqlite3.connect( "database.db" )
        conn.row_factory = sqlite3.Row
        return conn

    def insert_map_entry(self, file_uuid, file_ext, file_width, file_height):
        file_date = datetime.today().strftime('%Y-%m-%d')
        conn = self.get_db_connection()
        conn.execute( '''
            INSERT INTO maps ( file_uuid, file_date, file_ext, file_width, file_height ) VALUES ( ?, ?, ?, ?, ? )
        ''', ( file_uuid, file_date, file_ext, file_width, file_height ) )

    def create_tables(self):
        conn = self.get_db_connection()
        conn.execute( '''CREATE TABLE IF NOT EXISTS maps( 
            ID INT PRIMARY KEY NOT NULL,
            file_uuid   text,
            file_date   date,
            file_ext    text,
            file_width  int,
            file_height int
        )''')
        conn.commit()
        conn.close()

    def get_paths(self):
        conn = self.get_db_connection()
        paths= conn.execute( 'SELECT * FROM paths' ).fetchall()
        conn.close()
        if paths is None:
            return False
        return paths

