from statsmodels.tsa.stattools import adfuller


def adf_test(series):
    if len(series) < 20:
        return None

    result = adfuller(series.dropna())

    return {
        "adf_stat": result[0],
        "p_value": result[1],
        "lags": result[2],
        "n_obs": result[3],
        "critical_values": result[4]
    }
