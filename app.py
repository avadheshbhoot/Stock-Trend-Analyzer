import streamlit as st

from scanner import scan_market
from chart import show_chart
from ui import (
    init_session,
    show_results,
)

# ==========================================================
# PAGE
# ==========================================================

st.set_page_config(
    page_title="Stock Trend Analyzer V2",
    page_icon="📈",
    layout="wide",
)

init_session()

st.title("📈 Stock Trend Analyzer V2")

st.write(
"""
Find trending stocks using Moving Average analysis.

Supports scanning all NSE F&O stocks or analysing a single stock.
"""
)

st.divider()

# ==========================================================
# PARAMETERS
# ==========================================================

st.subheader("Parameters")

c1, c2, c3 = st.columns(3)

with c1:

    ma_period = st.number_input(
        "Moving Average",
        value=50,
        min_value=5,
        step=5,
    )

with c2:

    interval = st.selectbox(
        "Interval",
        [
            "5m",
            "15m",
            "30m",
            "1h",
            "1d",
        ],
        index=1,
    )

with c3:

    period = st.selectbox(
        "Period",
        [
            "5d",
            "1mo",
            "3mo",
            "6mo",
            "1y",
        ],
        index=0,
    )

st.divider()

# ==========================================================
# MODE
# ==========================================================

mode = st.radio(
    "Scan Type",
    [
        "F&O Stocks",
        "Manual Stock",
    ],
    horizontal=True,
)

manual_symbol = ""

if mode == "Manual Stock":

    manual_symbol = st.text_input(
        "Stock Symbol",
        placeholder="RELIANCE"
    ).upper()

    run = st.button(
        "📈 Analyse Stock",
        type="primary",
    )

else:

    run = st.button(
        "🔍 Scan F&O Stocks",
        type="primary",
    )

st.divider()

# ==========================================================
# PLACEHOLDERS
# ==========================================================

progress_bar = st.empty()

status_text = st.empty()

# ==========================================================
# Progress Callback
# ==========================================================

def update_progress(current, total, symbol):

    progress_bar.progress(current / total)

    status_text.info(
        f"Processing {symbol} ({current}/{total})"
    )

# ==========================================================
# MANUAL STOCK
# ==========================================================

if run and mode == "Manual Stock":

    if manual_symbol == "":

        st.warning("Please enter a symbol.")

    else:

        st.session_state.selected_symbol = manual_symbol

# ==========================================================
# F&O SCAN
# ==========================================================

if run and mode == "F&O Stocks":

    results = scan_market(

        period=period,

        interval=interval,

        ma_period=ma_period,

        progress_callback=update_progress,

    )

    st.session_state.scan_results = results

    progress_bar.empty()

    status_text.empty()

# ==========================================================
# RESULTS
# ==========================================================

if not st.session_state.scan_results.empty:

    symbol = show_results(

        st.session_state.scan_results

    )

# ==========================================================
# CHART
# ==========================================================

if st.session_state.selected_symbol:

    st.divider()

    show_chart(

        st.container(),

        st.session_state.selected_symbol,

        period,

        interval,

        ma_period,

    )
