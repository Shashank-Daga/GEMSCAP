# Real-Time Quant Analytics Dashboard

## Objective
This project is a real-time quantitative analytics application designed as a prototype for
traders and researchers at a quantitative trading firm. The system ingests live tick-level
market data, performs statistical analytics commonly used in relative value and
mean-reversion strategies, and visualizes results through an interactive dashboard.

The application demonstrates an end-to-end workflow:
- Real-time data ingestion
- Persistent storage
- Time-based resampling
- Quantitative analytics
- Interactive visualization
- Alerts and data export

---

## Tech Stack
- **Backend & Frontend:** Streamlit (Python)
- **Data Source:** Binance Futures WebSocket (`@trade`)
- **Storage:** SQLite
- **Analytics:** pandas, numpy, statsmodels
- **Visualization:** Plotly
- **Concurrency:** asyncio + threading

---

## Application Architecture

The system is modular and loosely coupled:

1. **Ingestion Layer**
   - Connects to Binance Futures WebSocket
   - One WebSocket per symbol
   - Normalizes tick data: `{timestamp, symbol, price, size}`
   - Persists data into SQLite

2. **Storage Layer**
   - SQLite database for raw ticks
   - Lightweight and persistent
   - Enables reproducible analytics and resampling

3. **Analytics Layer**
   - Time-based resampling (1s, 1m, 5m)
   - OLS regression for hedge ratio estimation
   - Spread construction
   - Z-score computation (rolling window)
   - Rolling correlation
   - ADF test for stationarity

4. **Visualization Layer**
   - Interactive dashboard built with Streamlit and Plotly
   - Price comparison, spread, z-score, correlation
   - Zoom, pan, hover supported

5. **Alerting & Export**
   - Rule-based z-score alerts
   - CSV export for processed analytics and resampled data

---

## Analytics Methodology

### Hedge Ratio
Computed using Ordinary Least Squares regression:

Price_A = α + β × Price_B

The hedge ratio β is used to construct the spread.

### Spread
Spread = Price_A − β × Price_B

### Z-Score
Z = (Spread − rolling_mean) / rolling_std


Used for mean-reversion signals.

### Rolling Correlation
Measures short-term co-movement between the two assets.

### ADF Test
Used to test stationarity of the spread series.

---

## Running the Application

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the app
```bash
streamlit run app.py
```

---

## Design Decisions & Trade-offs

- **Streamlit** was chosen for rapid prototyping and interactive analytics.
- **SQLite** provides lightweight persistence suitable for a single-user prototype.
- Analytics are computed on-demand to avoid unnecessary recomputation.
- User-triggered execution balances responsiveness and system stability.

These trade-offs were made intentionally to prioritize clarity, correctness,
and extensibility over production-grade latency.

