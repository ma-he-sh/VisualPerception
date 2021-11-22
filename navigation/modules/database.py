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

    def insert_map_entry(self, file_uuid, file_name, file_ext, file_width, file_height):
        file_date = datetime.today().strftime('%Y-%m-%d')
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute( '''
            INSERT INTO maps ( file_uuid, file_name, file_date, file_ext, file_width, file_height ) VALUES ( ?, ?, ?, ?, ?, ? )
        ''', ( file_uuid, file_name, file_date, file_ext, file_width, file_height ) )
        conn.commit()
        conn.close()

    def create_tables(self):
        conn = self.get_db_connection()
        conn.execute( '''CREATE TABLE IF NOT EXISTS maps( 
            ID integer primary key,
            file_uuid   text,
            file_name   text,
            file_date   date,
            file_ext    text,
            file_width  text,
            file_height text
        )''')
        conn.commit()
        conn.close()

    def get_entry(self, file_uuid):
        conn = self.get_db_connection()
        row = conn.execute("SELECT * FROM maps WHERE file_uuid='%s'" % file_uuid ).fetchone()
        conn.close()
        if row is None:
            return False
        return row

    def delete_entry(self, file_uuid):
        conn = self.get_db_connection()
        conn.execute("DELETE FROM maps WHERE file_uuid='%s'" % file_uuid )
        conn.commit()
        conn.close()

    def get_paths(self):
        maps = []
        conn = self.get_db_connection()
        rows= conn.execute( 'SELECT * FROM maps' ).fetchall()
        for map in rows:
            maps.append({
                'ID': map[0],
                'file_uuid': map[1],
                'file_name': map[2],
                'file_date': map[3],
                'file_ext' : map[4],
                'file_width': map[5],
                'file_height': map[6]
            })
        conn.close()
        if rows is None:
            return False
        return maps

