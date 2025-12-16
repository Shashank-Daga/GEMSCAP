import pandas as pd
import numpy as np


def compute_spread(df, symbol_a, symbol_b, hedge_ratio):
    a = df[df["symbol"] == symbol_a].set_index("ts")["price_close"]
    b = df[df["symbol"] == symbol_b].set_index("ts")["price_close"]

    merged = pd.concat([a, b], axis=1).dropna()
    merged.columns = ["A", "B"]

    merged["spread"] = merged["A"] - hedge_ratio * merged["B"]
    return merged


def compute_zscore(series, window):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std


def compute_rolling_correlation(df, symbol_a, symbol_b, window):
    a = df[df["symbol"] == symbol_a].set_index("ts")["price_close"]
    b = df[df["symbol"] == symbol_b].set_index("ts")["price_close"]

    merged = pd.concat([a, b], axis=1).dropna()
    return merged["A"].rolling(window).corr(merged["B"])


def price_statistics(series):
    return {
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max())
    }
