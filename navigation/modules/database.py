import sqlite3

class DB:
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
            return false
        return data

    def close(self):
        self.conn.close()

def get_db_connection():
    conn = sqlite3.connect( "database.db" )
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute( '''CREATE TABLE maps
            ( ID INT PRIMARY KEY NOT NULL,
            file_uuid   CHAR( 36 ),
            file_date   DATE    DEFAILT now(),
            file_ext    CHAR( 10 ),
            file_width  CHAR( 4 ),
            file_height CHAR( 4 )
        );''')
    conn.commit()
    conn.close()

def get_paths():
    conn = get_db_connection()
    paths= conn.execute( 'SELECT * FROM paths' ).fetchall()
    conn.close()
    if paths is None:
        return false
    return paths

def 
