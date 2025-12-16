from statsmodels.tsa.stattools import adfuller


def adf_test(series):
    """
    Perform Augmented Dickey-Fuller test for stationarity.

    The ADF test checks the null hypothesis that a unit root is present
    in the time series (i.e., the series is non-stationary).

    Interpretation:
    - p-value < 0.05: Reject null hypothesis → Series is stationary
    - p-value >= 0.05: Fail to reject → Series is non-stationary

    Args:
        series: Pandas Series of values (typically spread)

    Returns:
        Dictionary with test results, or None if insufficient data
    """
    clean_series = series.dropna()

    if len(clean_series) < 20:
        return None

    result = adfuller(clean_series)

    return {
        "adf_stat": float(result[0]),
        "p_value": float(result[1]),
        "lags": int(result[2]),
        "n_obs": int(result[3]),
        "critical_values": {
            "1%": float(result[4]["1%"]),
            "5%": float(result[4]["5%"]),
            "10%": float(result[4]["10%"])
        },
        "is_stationary_5pct": result[1] < 0.05
    }
