import plotly.graph_objects as go


def plot_prices(df, symbol_a, symbol_b):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["ts"],
        y=df["A"],
        name=symbol_a,
        line=dict(width=2)
    ))

    fig.add_trace(go.Scatter(
        x=df["ts"],
        y=df["B"],
        name=symbol_b,
        line=dict(width=2)
    ))

    fig.update_layout(
        title="Price Comparison",
        xaxis_title="Time",
        yaxis_title="Price",
        hovermode="x unified"
    )

    return fig


def plot_spread_zscore(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["spread"],
        name="Spread",
        line=dict(color="blue")
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["zscore"],
        name="Z-Score",
        yaxis="y2",
        line=dict(color="red")
    ))

    fig.update_layout(
        title="Spread & Z-Score",
        xaxis_title="Time",
        yaxis_title="Spread",
        yaxis2=dict(
            title="Z-Score",
            overlaying="y",
            side="right"
        ),
        hovermode="x unified"
    )

    return fig


def plot_correlation(corr_series):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=corr_series.index,
        y=corr_series.values,
        name="Rolling Correlation",
        line=dict(color="green")
    ))

    fig.update_layout(
        title="Rolling Correlation",
        xaxis_title="Time",
        yaxis_title="Correlation",
        hovermode="x unified"
    )

    return fig
