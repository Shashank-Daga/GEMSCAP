import statsmodels.api as sm
import pandas as pd


def compute_hedge_ratio(df, symbol_a, symbol_b):
    """
    OLS regression: price_A ~ beta * price_B
    Returns hedge ratio (beta).
    """
    a = df[df["symbol"] == symbol_a]["price_close"]
    b = df[df["symbol"] == symbol_b]["price_close"]

    aligned = pd.concat([a, b], axis=1).dropna()
    aligned.columns = ["A", "B"]

    if len(aligned) < 20:
        return None

    X = sm.add_constant(aligned["B"])
    model = sm.OLS(aligned["A"], X).fit()

    return model.params["B"]
