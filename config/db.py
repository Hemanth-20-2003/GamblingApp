# db.py - Manual MySQL connection (no ORM)
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",         # Change to your MySQL username
    "password": "Hemanth@12",  # Change to your MySQL password
    "database": "gambling_app",
    "autocommit": False,
}

def get_connection():
    """Return a new MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise ConnectionError(f"MySQL connection failed: {e}")

def execute_query(conn, query, params=None, fetch=False):
    """
    Execute a query on an existing connection.
    Returns lastrowid for INSERT, rows for SELECT, rowcount otherwise.
    """
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        return cursor
    finally:
        cursor.close()

def execute_one(conn, query, params=None):
    """Execute SELECT and return first row as dict, or None."""
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchone()
    finally:
        cursor.close()

def insert(conn, query, params=None):
    """Execute INSERT and return the new row's id."""
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        return cursor.lastrowid
    finally:
        cursor.close()
