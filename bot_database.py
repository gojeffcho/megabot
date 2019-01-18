import sqlite3
import sys

from bot_config import CONFIG

conn = sqlite3.connect(CONFIG['DatabaseFile'])
cursor = conn.cursor()


def get_db_user(conn, cursor, user):
  """Check if a given user exists in the database.
  
  Args:
    conn (sqlite3.Connection)
      SQLite 3 connection.
    
    cursor (sqlite3.Cursor)
      SQLite3 cursor.
    
    user (discord.Member)
      The user to look up.
  
  Returns:
    result
    A sqlite3.Row object if a match was found; otherwise None.
  """
  cmd = 'SELECT * FROM users WHERE id == ?'
  params = (user.id,)
  cursor.execute(cmd, params)
  result = cursor.fetchone()
  
  return result
  
  
def init():
  """Create the databases."""
  
  cmd   = """CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY,
              username TEXT NOT NULL, 
              points INTEGER, 
              level TEXT, 
              times_capped INTEGER
             );"""
  
  cursor.execute(cmd)
  conn.commit()
  
  cmd   = """CREATE TABLE IF NOT EXISTS notes (
              id INTEGER,
              datetime INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              user_name TEXT NOT NULL,
              type TEXT NOT NULL, 
              desc TEXT NOT NULL,
              PRIMARY KEY (id, user_id)
             );"""
            
  cursor.execute(cmd)
  conn.commit()
  
  cmd   = """CREATE TABLE IF NOT EXISTS events (
              id INTEGER PRIMARY KEY, 
              user_id INTEGER, 
              type TEXT,
              expiry INTEGER, 
              callback TEXT
             );"""
             
  cursor.execute(cmd)
  conn.commit()


def reset():
  """DEBUGGING: Delete all databases to reinitialize them."""

  cmd   = """DROP TABLE IF EXISTS users;"""
  cursor.execute(cmd)
  conn.commit()
  
  cmd   = """DROP TABLE IF EXISTS notes;"""
  cursor.execute(cmd)
  conn.commit()
  
  cmd   = """DROP TABLE IF EXISTS events;"""
  cursor.execute(cmd)
  conn.commit()
  
  
  
if __name__ == '__main__':
  if '-r' in sys.argv:
    reset()

  init()
  
  
  
  