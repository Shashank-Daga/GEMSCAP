import streamlit as st
import asyncio
import threading
import pandas as pd

from ingestion.binance_ws import start_stream
from storage.db import init_db

from analytics.sampling import load_ticks, resample_ticks
from analytics.regression import compute_hedge_ratio
from analytics.stats import (
    compute_spread,
    compute_zscore,
    compute_rolling_correlation,
    price_statistics
)
from analytics.stationarity import adf_test

from ui.plots import (
    plot_prices,
    plot_spread_zscore,
    plot_correlation
)

from alerts.rules import check_zscore_alert


st.set_page_config(page_title="Quant Analytics App", layout="wide")

st.title("Real-Time Quant Analytics Dashboard")

# Initialize DB
init_db()

st.sidebar.header("Data Ingestion")

symbols_input = st.sidebar.text_input(
    "Symbols (comma-separated)",
    value="btcusdt,ethusdt"
)

if "ingestion_running" not in st.session_state:
    st.session_state.ingestion_running = False


def run_ingestion(symbols):
    asyncio.run(start_stream(symbols))


if st.sidebar.button("Start Ingestion"):
    if not st.session_state.ingestion_running:
        symbols = [s.strip().lower() for s in symbols_input.split(",") if s.strip()]
        t = threading.Thread(
            target=run_ingestion,
            args=(symbols,),
            daemon=True
        )
        t.start()
        st.session_state.ingestion_running = True
        st.sidebar.success("Ingestion started")

if st.sidebar.button("Stop Ingestion"):
    st.warning("Stop functionality will be refined later.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Analytics Controls")
st.sidebar.info("Use 'Run Analytics' to refresh live metrics.")

st.info("Phase 1 & 2 complete: Live tick ingestion running in background.")

st.subheader("Data Preview")

symbols = [s.strip().lower() for s in symbols_input.split(",") if s.strip()]

timeframe = st.selectbox(
    "Select Timeframe",
    ["1s", "1m", "5m"],
    index=1
)

if st.button("Load & Resample Data"):
    raw_df = load_ticks(symbols)

    if raw_df.empty:
        st.warning("No tick data available yet.")
    else:
        resampled_df = resample_ticks(raw_df, timeframe)

        if resampled_df.empty:
            st.warning("Not enough data to resample.")
        else:
            st.dataframe(resampled_df.tail(20))

st.subheader("Quant Analytics")

st.caption(
    "Analytics computed on resampled Binance Futures trade data. "
    "Charts support zoom, pan, and hover for exploratory analysis."
)

symbol_a = st.selectbox("Symbol A", symbols)
symbol_b = st.selectbox("Symbol B", symbols, index=1)

rolling_window = st.slider(
    "Rolling Window",
    min_value=10,
    max_value=200,
    value=50
)

alert_threshold = st.number_input(
    "Z-Score Alert Threshold",
    min_value=0.5,
    max_value=5.0,
    value=2.0,
    step=0.1
)

if st.button("Run Analytics"):

    raw_df = load_ticks(symbols)
    resampled_df = resample_ticks(raw_df, timeframe)

    hedge = compute_hedge_ratio(resampled_df, symbol_a.upper(), symbol_b.upper())

    if hedge is None:
        st.warning("Not enough data for regression.")
    else:
        spread_df = compute_spread(
            resampled_df, symbol_a.upper(), symbol_b.upper(), hedge
        )

        spread_df["zscore"] = compute_zscore(
            spread_df["spread"], rolling_window
        )

        corr = compute_rolling_correlation(
            resampled_df, symbol_a.upper(), symbol_b.upper(), rolling_window
        )

        # ---------- LIVE SUMMARY STATS (NOW SAFE) ----------
        st.subheader("Live Summary Stats")

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Spread", round(spread_df["spread"].iloc[-1], 4))
        col2.metric("Latest Z-Score", round(spread_df["zscore"].iloc[-1], 2))
        col3.metric(
            "Rolling Correlation",
            round(corr.dropna().iloc[-1], 2) if corr is not None else None
        )

        # ---------- ALERT ----------
        alert = check_zscore_alert(spread_df["zscore"], alert_threshold)

        if alert and alert["triggered"]:
            st.error(
                f"ALERT: |Z-Score| = {alert['value']:.2f} "
                f"exceeded threshold {alert['threshold']}"
            )
        else:
            st.success(
                f"Z-Score OK: {alert['value']:.2f} "
                f"(threshold {alert['threshold']})"
            )

        # ---------- VISUAL ANALYTICS ----------
        st.subheader("Visual Analytics")

        price_fig = plot_prices(
            spread_df.reset_index().rename(columns={"index": "ts"}),
            symbol_a.upper(),
            symbol_b.upper()
        )
        st.plotly_chart(price_fig, use_container_width=True)

        spread_fig = plot_spread_zscore(spread_df)
        st.plotly_chart(spread_fig, use_container_width=True)

        if corr is not None:
            corr_fig = plot_correlation(corr)
            st.plotly_chart(corr_fig, use_container_width=True)

        # ---------- STATS ----------
        st.metric("Hedge Ratio", round(hedge, 4))

        stats_a = price_statistics(spread_df["A"])
        stats_b = price_statistics(spread_df["B"])

        st.write("Price Stats — Symbol A", stats_a)
        st.write("Price Stats — Symbol B", stats_b)

        if st.button("Run ADF Test on Spread"):
            adf = adf_test(spread_df["spread"])
            if adf:
                st.json(adf)

        # ---------- DATA EXPORT ----------
        st.subheader("Data Export")

        csv_spread = spread_df.reset_index().to_csv(index=False)
        st.download_button(
            label="Download Spread & Z-Score CSV",
            data=csv_spread,
            file_name="spread_analytics.csv",
            mime="text/csv"
        )

        csv_resampled = resampled_df.to_csv(index=False)
        st.download_button(
            label="Download Resampled Price Data CSV",
            data=csv_resampled,
            file_name="resampled_prices.csv",
            mime="text/csv"
        )
