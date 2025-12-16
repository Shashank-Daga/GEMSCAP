import plotly.graph_objects as go


def plot_prices(df, symbol_a, symbol_b):
    """
    Plot price comparison for two symbols.

    Args:
        df (pd.DataFrame):
            DataFrame indexed by timestamp (ts) with columns named after symbols.
            Expected columns: [symbol_a, symbol_b]
        symbol_a (str):
            First trading symbol (e.g. "ETHUSDT")
        symbol_b (str):
            Second trading symbol (e.g. "BTCUSDT")

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[symbol_a],
        name=symbol_a,
        line=dict(width=2, color='#3b82f6'),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[symbol_b],
        name=symbol_b,
        line=dict(width=2, color='#f59e0b'),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="Price Comparison",
        xaxis_title="Time",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_dark",
        height=400,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig


def plot_spread_zscore(df, threshold=2.0):
    """
    Plot spread and z-score with threshold lines.

    Args:
        df: DataFrame with index as timestamp and columns 'spread', 'zscore'
        threshold: Z-score threshold for alert lines

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Spread trace
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["spread"],
        name="Spread",
        line=dict(color="#3b82f6", width=2),
        yaxis="y1",
        hovertemplate='Spread: %{y:.4f}<extra></extra>'
    ))

    # Z-Score trace
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["zscore"],
        name="Z-Score",
        line=dict(color="#ef4444", width=2),
        yaxis="y2",
        hovertemplate='Z-Score: %{y:.2f}<extra></extra>'
    ))

    # Add threshold lines on z-score axis
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="rgba(239, 68, 68, 0.5)",
        annotation_text=f"+{threshold}σ",
        annotation_position="right",
        yref="y2"
    )

    fig.add_hline(
        y=-threshold,
        line_dash="dash",
        line_color="rgba(239, 68, 68, 0.5)",
        annotation_text=f"-{threshold}σ",
        annotation_position="right",
        yref="y2"
    )

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="rgba(156, 163, 175, 0.3)",
        yref="y2"
    )

    fig.update_layout(
        title="Spread & Z-Score Evolution",
        xaxis_title="Time",
        yaxis=dict(
            title=dict(
                text="Spread",
                font=dict(color="#3b82f6")
            ),
            tickfont=dict(color="#3b82f6")
        ),
        yaxis2=dict(
            title=dict(
                text="Z-Score",
                font=dict(color="#ef4444")
            ),
            tickfont=dict(color="#ef4444"),
            overlaying="y",
            side="right"
        ),
        hovermode="x unified",
        template="plotly_dark",
        height=450,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig


def plot_correlation(corr_series):
    """
    Plot rolling correlation between two assets.

    Args:
        corr_series: Pandas Series with timestamp index and correlation values

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=corr_series.index,
        y=corr_series.values,
        name="Rolling Correlation",
        line=dict(color="#10b981", width=2),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)',
        hovertemplate='Correlation: %{y:.3f}<extra></extra>'
    ))

    # Add reference lines
    fig.add_hline(
        y=1,
        line_dash="dot",
        line_color="rgba(156, 163, 175, 0.3)",
        annotation_text="Perfect Correlation",
        annotation_position="right"
    )

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="rgba(156, 163, 175, 0.5)"
    )

    fig.add_hline(
        y=-1,
        line_dash="dot",
        line_color="rgba(156, 163, 175, 0.3)",
        annotation_text="Perfect Negative",
        annotation_position="right"
    )

    fig.update_layout(
        title="Rolling Correlation",
        xaxis_title="Time",
        yaxis_title="Correlation Coefficient",
        hovermode="x unified",
        template="plotly_dark",
        height=400,
        yaxis=dict(range=[-1.1, 1.1])
    )

    return fig
