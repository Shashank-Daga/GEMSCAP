import streamlit as st
import asyncio
import threading
import pandas as pd
from sqlalchemy import text

from ingestion.binance_ws import start_stream
from storage.db import init_db, engine

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

st.title("🔬 Real-Time Quant Analytics Dashboard")

# Initialize DB
init_db()

# Initialize session state
if "ingestion_running" not in st.session_state:
    st.session_state.ingestion_running = False
if "ingestion_task" not in st.session_state:
    st.session_state.ingestion_task = None
if "stop_event" not in st.session_state:
    st.session_state.stop_event = None


def run_ingestion(symbols, stop_event):
    """Run ingestion with stop event support"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_stream(symbols, stop_event))
    except Exception as e:
        st.error(f"Ingestion error: {e}")
    finally:
        loop.close()


# Sidebar - Data Ingestion Controls
st.sidebar.header("📡 Data Ingestion")

symbols_input = st.sidebar.text_input(
    "Symbols (comma-separated)",
    value="btcusdt,ethusdt",
    help="Enter Binance Futures symbols in lowercase"
)

# System Status Indicator
st.sidebar.markdown("### System Status")
if st.session_state.ingestion_running:
    st.sidebar.success("🟢 Ingestion Active")
else:
    st.sidebar.error("🔴 Ingestion Stopped")

# Database Statistics
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM ticks"))
        tick_count = result.scalar()
        st.sidebar.metric("Total Ticks Stored", f"{tick_count:,}")
except:
    st.sidebar.metric("Total Ticks Stored", "N/A")

# Start/Stop Controls
col_start, col_stop = st.sidebar.columns(2)

with col_start:
    if st.button("▶️ Start", use_container_width=True):
        if not st.session_state.ingestion_running:
            symbols = [s.strip().lower() for s in symbols_input.split(",") if s.strip()]
            if not symbols:
                st.sidebar.error("Please enter at least one symbol")
            else:
                st.session_state.stop_event = threading.Event()
                t = threading.Thread(
                    target=run_ingestion,
                    args=(symbols, st.session_state.stop_event),
                    daemon=True
                )
                t.start()
                st.session_state.ingestion_task = t
                st.session_state.ingestion_running = True
                st.sidebar.success(f"Started ingestion for: {', '.join(symbols)}")
                st.rerun()

with col_stop:
    if st.button("⏹️ Stop", use_container_width=True):
        if st.session_state.ingestion_running and st.session_state.stop_event:
            st.session_state.stop_event.set()
            st.session_state.ingestion_running = False
            st.sidebar.info("Ingestion stopped")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Analytics Controls")
st.sidebar.info("Configure parameters below and click 'Run Analytics' to refresh metrics.")

# Main Content
st.info("💡 **Live tick ingestion running in background** - Start ingestion to collect data, then run analytics.")

# Parse symbols
symbols = [s.strip().lower() for s in symbols_input.split(",") if s.strip()]

# Data Preview Section
with st.expander("📊 Data Preview", expanded=False):
    timeframe_preview = st.selectbox(
        "Select Timeframe for Preview",
        ["1s", "1m", "5m"],
        index=1,
        key="preview_timeframe"
    )

    if st.button("Load & Preview Data"):
        with st.spinner("Loading data..."):
            raw_df = load_ticks(symbols)

            if raw_df.empty:
                st.warning("⚠️ No tick data available yet. Make sure ingestion is running and symbols are correct.")
                st.info(f"Currently tracking: {', '.join(symbols)}")
            else:
                st.success(f"✅ Loaded {len(raw_df):,} ticks")
                resampled_df = resample_ticks(raw_df, timeframe_preview)

                if resampled_df.empty:
                    st.warning("Not enough data to resample.")
                else:
                    st.dataframe(
                        resampled_df.tail(20),
                        use_container_width=True,
                        height=300
                    )

st.markdown("---")
st.subheader("📈 Quantitative Analytics")

st.caption(
    "Analytics computed on resampled Binance Futures trade data. "
    "Charts support zoom, pan, and hover for exploratory analysis."
)

# Analytics Configuration
col1, col2, col3 = st.columns(3)

with col1:
    timeframe = st.selectbox(
        "Timeframe",
        ["1s", "1m", "5m"],
        index=1,
        help="Resampling timeframe for analytics"
    )

with col2:
    # Ensure two different symbols by default
    if len(symbols) < 2:
        st.error("⚠️ Please enter at least 2 symbols for pair analytics")
        st.stop()

    symbol_a = st.selectbox("Symbol A", symbols, index=0)

with col3:
    # Filter out symbol_a from choices for symbol_b
    symbols_b = [s for s in symbols if s != symbol_a]
    if not symbols_b:
        st.error("⚠️ Symbol A and B cannot be the same")
        st.stop()

    symbol_b = st.selectbox("Symbol B", symbols_b, index=0)

col4, col5 = st.columns(2)

with col4:
    rolling_window = st.slider(
        "Rolling Window",
        min_value=10,
        max_value=200,
        value=50,
        help="Window size for rolling statistics"
    )

with col5:
    alert_threshold = st.number_input(
        "Z-Score Alert Threshold",
        min_value=0.5,
        max_value=5.0,
        value=2.0,
        step=0.1,
        help="Alert when |z-score| exceeds this value"
    )

# Run Analytics Button
if st.button("🚀 Run Analytics", type="primary", use_container_width=True):

    with st.spinner("📥 Loading data..."):
        raw_df = load_ticks(symbols)

        if raw_df.empty:
            st.error("❌ No data available. Please start ingestion and wait for data collection.")
            st.stop()

        resampled_df = resample_ticks(raw_df, timeframe)

        if resampled_df.empty:
            st.error("❌ Not enough data to resample. Please wait for more data.")
            st.stop()

    with st.spinner("🔬 Computing analytics..."):
        hedge = compute_hedge_ratio(resampled_df, symbol_a.upper(), symbol_b.upper())

    if hedge is None:
        st.warning("⚠️ Not enough data for regression analysis. Need at least 40 data points.")
        st.info(f"Current resampled data points: {len(resampled_df)}")
        st.stop()

    # Compute all analytics
    spread_df = compute_spread(
        resampled_df, symbol_a.upper(), symbol_b.upper(), hedge
    )

    if spread_df.empty or len(spread_df) < rolling_window:
        st.error(f"❌ Insufficient data for rolling window analysis. Need at least {rolling_window} points.")
        st.stop()

    spread_df["zscore"] = compute_zscore(spread_df["spread"], rolling_window)

    corr = compute_rolling_correlation(
        resampled_df, symbol_a.upper(), symbol_b.upper(), rolling_window
    )

    # ========== LIVE SUMMARY STATS ==========
    st.subheader("📊 Live Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Latest Spread",
            f"{spread_df['spread'].iloc[-1]:.4f}"
        )

    with col2:
        latest_zscore = spread_df["zscore"].dropna()
        if not latest_zscore.empty:
            st.metric(
                "Latest Z-Score",
                f"{latest_zscore.iloc[-1]:.2f}"
            )
        else:
            st.metric("Latest Z-Score", "N/A")

    with col3:
        if corr is not None and not corr.dropna().empty:
            st.metric(
                "Rolling Correlation",
                f"{corr.dropna().iloc[-1]:.3f}"
            )
        else:
            st.metric("Rolling Correlation", "N/A")

    with col4:
        st.metric(
            "Hedge Ratio (β)",
            f"{hedge:.4f}"
        )

    # ========== ALERT SYSTEM ==========
    alert = check_zscore_alert(spread_df["zscore"], alert_threshold)

    if alert and alert["triggered"] and alert["value"] is not None:
        st.error(
            f"🚨 **ALERT**: |Z-Score| = {abs(alert['value']):.2f} "
            f"exceeded threshold {alert['threshold']:.2f}"
        )
    elif alert and alert["value"] is not None:
        st.success(
            f"✅ Z-Score OK: {alert['value']:.2f} "
            f"(threshold: ±{alert['threshold']:.2f})"
        )
    else:
        st.info("ℹ️ Z-Score data unavailable")

    st.markdown("---")

    # ========== VISUAL ANALYTICS ==========
    st.subheader("📈 Visual Analytics")

    # Price Comparison Chart
    st.markdown("#### Price Comparison")
    price_fig = plot_prices(
        spread_df.reset_index().rename(columns={"index": "ts"}),
        symbol_a.upper(),
        symbol_b.upper()
    )
    st.plotly_chart(price_fig, use_container_width=True)

    # Spread & Z-Score Chart
    st.markdown("#### Spread & Z-Score Evolution")
    spread_fig = plot_spread_zscore(spread_df, alert_threshold)
    st.plotly_chart(spread_fig, use_container_width=True)

    # Rolling Correlation Chart
    if corr is not None and not corr.dropna().empty:
        st.markdown("#### Rolling Correlation")
        corr_fig = plot_correlation(corr)
        st.plotly_chart(corr_fig, use_container_width=True)
    else:
        st.info("ℹ️ Correlation data unavailable")

    st.markdown("---")

    # ========== DESCRIPTIVE STATISTICS ==========
    st.subheader("📋 Descriptive Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Price Statistics — {symbol_a.upper()}**")
        stats_a = price_statistics(spread_df["A"])
        stats_df_a = pd.DataFrame([stats_a]).T
        stats_df_a.columns = ["Value"]
        st.dataframe(stats_df_a, use_container_width=True)

    with col2:
        st.markdown(f"**Price Statistics — {symbol_b.upper()}**")
        stats_b = price_statistics(spread_df["B"])
        stats_df_b = pd.DataFrame([stats_b]).T
        stats_df_b.columns = ["Value"]
        st.dataframe(stats_df_b, use_container_width=True)

    # ========== ADVANCED ANALYTICS ==========
    with st.expander("🔬 Advanced Analytics - Stationarity Test", expanded=False):
        st.markdown("""
        **Augmented Dickey-Fuller Test**  
        Tests the null hypothesis that the spread series has a unit root (non-stationary).
        - **p-value < 0.05**: Reject null → Series is stationary (good for mean reversion)
        - **p-value ≥ 0.05**: Fail to reject → Series is non-stationary
        """)

        if st.button("Run ADF Test on Spread"):
            with st.spinner("Running ADF test..."):
                adf = adf_test(spread_df["spread"])
                if adf:
                    st.json(adf)

                    # Interpretation
                    if adf["p_value"] < 0.05:
                        st.success(
                            f"✅ **Stationary** (p-value: {adf['p_value']:.4f}) - "
                            "Spread shows mean-reverting behavior"
                        )
                    else:
                        st.warning(
                            f"⚠️ **Non-Stationary** (p-value: {adf['p_value']:.4f}) - "
                            "Spread may not be suitable for mean-reversion strategies"
                        )
                else:
                    st.error("Insufficient data for ADF test")

    # ========== DATA EXPORT ==========
    st.markdown("---")
    st.subheader("💾 Data Export")

    col1, col2 = st.columns(2)

    with col1:
        csv_spread = spread_df.reset_index().to_csv(index=False)
        st.download_button(
            label="📥 Download Spread & Z-Score CSV",
            data=csv_spread,
            file_name=f"spread_analytics_{symbol_a}_{symbol_b}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        csv_resampled = resampled_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Resampled Price Data CSV",
            data=csv_resampled,
            file_name=f"resampled_prices_{timeframe}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.caption("🔬 Real-Time Quantitative Analytics Dashboard | Built for Statistical Arbitrage & Mean-Reversion "
           "Strategies")
