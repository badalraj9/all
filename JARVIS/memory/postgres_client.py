import psycopg2
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import List, Dict, Any, Optional
import uuid
from loguru import logger

from JARVIS.core.config import settings

class PostgresClient:
    def __init__(self):
        self.conn = None
        self.connect()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD
            )
            self.conn.autocommit = True
            logger.info("Connected to PostgreSQL")
            self._init_schema()
        except Exception as e:
            logger.error(f"PostgreSQL Connection Failed: {e}")
            raise

    def _init_schema(self):
        """Idempotent schema initialization."""
        schema_path = settings.BASE_DIR / "memory" / "schema.sql"
        if not schema_path.exists():
            logger.warning("Schema file not found, skipping init.")
            return

        with open(schema_path, "r") as f:
            sql = f.read()

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql)
            logger.info("Database schema initialized.")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")

    def execute(self, query: str, params: tuple = None) -> None:
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
        except Exception as e:
            logger.error(f"Query execution failed: {e} | Query: {query}")
            raise

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Fetch one failed: {e}")
            return None

    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Fetch all failed: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()

# Singleton
db = PostgresClient()
