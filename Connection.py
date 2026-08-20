import os
from dotenv import load_dotenv
import atexit
from psycopg_pool import pool
from typing import Generator
from contextlib import contextmanager

# Load environment variables from the .env file
load_dotenv()

# Retrieve the variables (matching the names in your .env file)
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST", "localhost")  # Defaults to localhost if not in .env
DB_PORT = os.getenv("DB_PORT", "5432")       # Defaults to 5432 if not in .env

class Connection:
    _instance: "Connection | None" = None
    _pool: pool.ConnectionPool | None = None
    _dbinfo = f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} port={DB_PORT} host={DB_HOST}"

    def __new__(cls) -> "Connection | None":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialise(cls) -> "Connection | None":
        """Create the connection pool. Must be called once at application startup."""
        instance = cls.get_instance()
        if cls._pool is None:
            cls._pool = pool.ConnectionPool(cls._dbinfo)
            atexit.register(cls.close_pool)
        return instance

    @classmethod
    def close_pool(cls) -> None:
        """Close the connection pool."""
        if cls._pool is not None:
            cls._pool.close()
            cls._pool = None

    @classmethod
    def get_instance(cls) -> "Connection | None":
        """Return the singleton instance (pool may not be initialized yet)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        Tear down the pool and reset the singleton.
        Intended for test isolation — do NOT call in production.
        """
        if cls._pool:
            cls._pool.close()
        cls._pool = None
        cls._instance = None

    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager that yields a connection from the pool.

        The connection is returned to the pool on exit.
        On exception, the transaction is rolled back automatically.

        Example:
            with DatabasePool.get_instance().get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM creature")
        """
        if self._pool is None:
            raise RuntimeError("Connection not initialised. Call Connection.initialise(dsn) first.")

        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    @contextmanager
    def get_cursor(self) -> Generator:
        """
        Convenience context manager that yields a cursor directly.

        Args:
            use_dict_cursor: If True (default), rows are returned as dicts.
        """

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                yield cur

#     @classmethod
#     def test_db(cls):
#         sql = """
# CREATE TABLE IF NOT EXISTS test (id Serial PRIMARY KEY, name VARCHAR(255))
# """
#         with cls._instance.get_cursor() as cur:
#             cur.execute(sql)
#
#     @classmethod
#     def end_test_db(cls):
#         sql = """
#               DROP TABLE IF EXISTS test
#               """
#         with cls._instance.get_cursor() as cur:
#             cur.execute(sql)


