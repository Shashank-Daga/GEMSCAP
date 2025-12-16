def check_zscore_alert(zscore_series, threshold):
    """
    Checks if the latest z-score breaches the threshold.
    """
    clean = zscore_series.dropna()
    if clean.empty:
        return {"triggered": False, "value": None, "threshold": threshold}

    latest = float(clean.iloc[-1])
    return {
        "triggered": abs(latest) >= threshold,
        "value": latest,
        "threshold": threshold
    }
