from sqlalchemy import create_engine, text
from contextlib import contextmanager

# Database configuration
DB_PATH = "data/ticks.db"
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    future=True
)


@contextmanager
def get_connection():
    """
    Context manager for database connections.
    Ensures proper connection lifecycle handling.
    """
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Initialize database schema and indexes.
    """
    with get_connection() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                size REAL NOT NULL
            )
        """))

        # Index to optimize symbol + time-based queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_ticks_symbol_ts
            ON ticks (symbol, ts)
        """))

        conn.commit()


def insert_tick(ts, symbol, price, size):
    """
    Insert a single tick into the database.
    """
    with get_connection() as conn:
        conn.execute(
            text("""
                INSERT INTO ticks (ts, symbol, price, size)
                VALUES (:ts, :symbol, :price, :size)
            """),
            {
                "ts": ts,
                "symbol": symbol,
                "price": price,
                "size": size
            }
        )
        conn.commit()


def insert_tick_batch(ticks):
    """
    Insert multiple ticks efficiently using executemany.
    Expects a list of dicts with keys: ts, symbol, price, size.
    """
    if not ticks:
        return

    with get_connection() as conn:
        conn.execute(
            text("""
                INSERT INTO ticks (ts, symbol, price, size)
                VALUES (:ts, :symbol, :price, :size)
            """),
            ticks
        )
        conn.commit()
