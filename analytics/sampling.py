import pandas as pd
from sqlalchemy import text
from storage.db import engine

VALID_TIMEFRAMES = {
    "1s": "1S",
    "1m": "1T",
    "5m": "5T"
}


def load_ticks(symbols, lookback_minutes=60):
    """
    Load raw tick data from SQLite for selected symbols.
    """
    placeholders = ",".join([f"'{s.upper()}'" for s in symbols])

    query = text(f"""
        SELECT ts, symbol, price, size
        FROM ticks
        WHERE symbol IN ({placeholders})
        ORDER BY ts ASC
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if df.empty:
        return df

    df["ts"] = pd.to_datetime(df["ts"])
    df.set_index("ts", inplace=True)

    return df


def resample_ticks(df, timeframe):
    """
    Resample tick data into OHLCV-like structure.
    """
    if df.empty or timeframe not in VALID_TIMEFRAMES:
        return pd.DataFrame()

    rule = VALID_TIMEFRAMES[timeframe]

    resampled = (
        df.groupby("symbol")
          .resample(rule)
          .agg(
              price_open=("price", "first"),
              price_high=("price", "max"),
              price_low=("price", "min"),
              price_close=("price", "last"),
              volume=("size", "sum")
          ).dropna().reset_index()
    )

    return resampled
