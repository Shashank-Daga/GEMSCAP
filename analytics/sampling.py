import pandas as pd
from sqlalchemy import text
from storage.db import engine

VALID_TIMEFRAMES = {
    "1s": "1s",
    "1m": "1min",
    "5m": "5min"
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
            AND ts >= datetime('now', '-{lookback_minutes} minutes')
        ORDER BY ts ASC
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if df.empty:
        return df

    df["ts"] = pd.to_datetime(df["ts"], format='ISO8601')
    df.set_index("ts", inplace=True)

    return df


# REPLACE THE ENTIRE FUNCTION with this:

def resample_ticks(df, timeframe):
    """
    Resample tick data into OHLCV-like structure.
    """
    if df.empty or timeframe not in VALID_TIMEFRAMES:
        return pd.DataFrame()

    rule = VALID_TIMEFRAMES[timeframe]

    # Process each symbol separately to avoid warnings
    resampled_list = []

    for symbol in df['symbol'].unique():
        symbol_df = df[df['symbol'] == symbol].copy()

        resampled_symbol = symbol_df.resample(rule).agg({
            'price': ['first', 'max', 'min', 'last'],
            'size': 'sum'
        })

        resampled_symbol.columns = ['price_open', 'price_high', 'price_low', 'price_close', 'volume']
        resampled_symbol['symbol'] = symbol
        resampled_symbol = resampled_symbol.reset_index()

        resampled_list.append(resampled_symbol)

    if resampled_list:
        resampled = pd.concat(resampled_list, ignore_index=True)
        resampled = resampled.dropna()
    else:
        resampled = pd.DataFrame()

    return resampled
