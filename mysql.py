'''This is a pretty thin wrapper around MySQLdb.
The bDebug thing is nice and will print out all the SQL statements that are sent.'''

import MySQLdb
from MySQLdb.cursors import SSCursor, Cursor

_mysql_user = 'root'
_mysql_pass = 'secretpw'

class CursorWrapper:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor
    def __iter__(self):
        while True:
            t = self.cursor.fetchone()
            if t:
                yield t
            else:
                return
    def insert_id(self):
        return self.db.insert_id()
    def affected_rows(self):
        return self.hDB.affected_rows()
    def close(self):
        self.cursor.close()
    def fetchone(self):
        return self.cursor.fetchone()
    def fetchall(self):
        return self.cursor.fetchall()
         
class Connection:
    def __init__(self, db_name):
        self.db_name = db_name
        
    def _execute(self, cursor_klass, command, args):
        db = MySQLdb.connect(host='localhost', user=_mysql_user, passwd=_mysql_pass, db=self.db_name, cursorclass=cursor_klass)
        cursor = db.cursor()
        cursor.execute(command, args)
        return CursorWrapper(db, cursor)

    def execute(self, command, *args):
        '''Returns a cursor that you can call fetchone() or fetchall() on.'''
        return self._execute(Cursor, command, args)
    
    def executeSS(self, sCommand, *args):
        '''Returns a cursor that you can call fetchone() or fetchall() on.'''
        return self._execute(SSCursor, command, args)

def Test():
    import time
    c = Connection('test')
    c.execute("DROP TABLE IF EXISTS pet");
    c.execute("CREATE TABLE IF NOT EXISTS pet (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(id), name VARCHAR(20), type VARCHAR(10));")
    foo = c.execute('INSERT INTO pet (name, type) VALUES (%s, %s);', 'Hannah', 'Dog')
    
    foo = c.execute('INSERT INTO pet (name, type) VALUES (%s, %s);', 'Chelsea', 'Dog')

    c.execute('INSERT INTO pet (name, type) VALUES (%s, %s);', 'Tuffy', 'Dog')
    c.execute('INSERT INTO pet (name, type) VALUES (%s, %s);', 'Barnaby', 'Rabbit')
    c.execute('INSERT INTO pet (name, type) VALUES (%s, %s);', 'Bob', 'Anole')
    c.execute('INSERT INTO pet (name, type) VALUES (%s, %s);', 'Sue', 'Anole')
    for (name,) in c.execute('SELECT (name) FROM pet WHERE type=%s', 'Dog'):
        print name
    print ''
    cCursor2 = c.execute('SELECT (name) FROM pet WHERE type=%s', 'Anole')
    for (name, ) in cCursor2:
        print name
    cur = c.execute('DELETE FROM pet WHERE type="Dog"')
    
            
if __name__ == '__main__':
    Test()
    print 'All done!'
