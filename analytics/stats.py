import pandas as pd
import numpy as np


def compute_spread(df, symbol_a, symbol_b, hedge_ratio):
    """
    Compute the spread between two symbols using a hedge ratio.

    Spread = Price_A - hedge_ratio * Price_B

    Args:
        df: Resampled DataFrame with columns 'symbol', 'ts', 'price_close'
        symbol_a: First symbol name
        symbol_b: Second symbol name
        hedge_ratio: Beta coefficient from OLS regression

    Returns:
        DataFrame with columns ['A', 'B', 'spread'] indexed by timestamp
    """
    a = df[df["symbol"] == symbol_a].set_index("ts")["price_close"]
    b = df[df["symbol"] == symbol_b].set_index("ts")["price_close"]

    merged = pd.concat([a, b], axis=1).dropna()
    merged.columns = ["A", "B"]

    merged["spread"] = merged["A"] - hedge_ratio * merged["B"]

    return merged


def compute_zscore(series, window):
    """
    Compute rolling z-score for a time series.

    Z-Score = (X - rolling_mean) / rolling_std

    Args:
        series: Pandas Series (typically spread values)
        window: Rolling window size

    Returns:
        Pandas Series of z-scores
    """
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()

    # Avoid division by zero
    zscore = (series - mean) / std

    return zscore


def compute_rolling_correlation(df, symbol_a, symbol_b, window):
    """
    Compute rolling correlation between two price series.

    Args:
        df: Resampled DataFrame with columns 'symbol', 'ts', 'price_close'
        symbol_a: First symbol name
        symbol_b: Second symbol name
        window: Rolling window size

    Returns:
        Pandas Series of correlation coefficients, or None if insufficient data
    """
    a = df[df["symbol"] == symbol_a].set_index("ts")["price_close"]
    b = df[df["symbol"] == symbol_b].set_index("ts")["price_close"]

    merged = pd.concat([a, b], axis=1).dropna()

    if len(merged) < window:
        return None

    merged.columns = ["A", "B"]

    return merged["A"].rolling(window).corr(merged["B"])


def price_statistics(series):
    """
    Compute descriptive statistics for a price series.

    Args:
        series: Pandas Series of prices

    Returns:
        Dictionary with mean, std, min, max
    """
    return {
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "median": float(series.median()),
        "range": float(series.max() - series.min())
    }
