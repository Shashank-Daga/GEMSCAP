def check_zscore_alert(zscore_series, threshold):
    """
    Checks if the latest z-score breaches the threshold.
    """
    if zscore_series.empty:
        return None

    latest = zscore_series.dropna().iloc[-1]

    if abs(latest) >= threshold:
        return {
            "triggered": True,
            "value": float(latest),
            "threshold": threshold
        }

    return {
        "triggered": False,
        "value": float(latest),
        "threshold": threshold
    }
