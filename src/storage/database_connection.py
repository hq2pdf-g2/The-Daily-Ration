import os
import threading
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

# TODO
# Thread-safe Singleton, dedicated purely to managing the connection state to Neon.

# Automatically load local .env variables at runtime
load_dotenv()  # <-- Add this

class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
                    cls._instance._setup(*args, **kwargs)
        return cls._instance

    def _setup(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("Database connection URL is missing.")
        
        print("Initializing Neon Connection Pool...")
        self.pool = ConnectionPool(
            conninfo=self.db_url,
            min_size=1,
            max_size=10,
            open=True
        )

    def get_connection(self):
        # Returns a context manager for a healthy connection from the pool.
        return self.pool.connection()

    def close(self):
        if hasattr(self, 'pool'):
            self.pool.close()
            print("Neon Connection Pool closed.")