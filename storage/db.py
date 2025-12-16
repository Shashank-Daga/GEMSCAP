from sqlalchemy import create_engine, text

DB_PATH = "data/ticks.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                size REAL NOT NULL
            )
        """))
        conn.commit()


def insert_tick(ts, symbol, price, size):
    with engine.connect() as conn:
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
