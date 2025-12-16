import statsmodels.api as sm


def compute_hedge_ratio(df, symbol_a, symbol_b, min_points=20):
    """
    Computes hedge ratio using OLS after aligning timestamps.
    """

    wide = (
        df[df["symbol"].isin([symbol_a, symbol_b])]
        .pivot(index="ts", columns="symbol", values="price_close")
        .dropna()
    )

    if len(wide) < min_points:
        return None

    y = wide[symbol_a]
    x = wide[symbol_b]

    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()

    return model.params[symbol_b]
