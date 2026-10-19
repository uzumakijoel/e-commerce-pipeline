import mysql.connector
from mysql.connector import Error
import sys
from contextlib import contextmanager
import logging

log=logging.getLogger(__name__)

@contextmanager
def db_connection(database,localhost,user,password):
    conn= None

    try:
        conn=mysql.connector.connect(
            database=database,
            host=localhost,
            user=user,
            password=password
        )
        yield conn
    except Error as e:
        log.error(type(e).__name__)
        log.warning("End of the pipeline")
        sys.exit(1)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            log.info("Database closed")

        