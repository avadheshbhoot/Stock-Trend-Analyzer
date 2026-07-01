import streamlit as st
import pandas as pd

# ==========================================================
# PAGE
# ==========================================================

st.set_page_config(
    page_title="Stock Trend Analyzer V2",
    page_icon="📈",
    layout="wide",
)

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

# ==========================================================
# MANUAL
# ==========================================================

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

progress_placeholder = st.empty()

results_placeholder = st.empty()

chart_placeholder = st.empty()

# ==========================================================
# MANUAL
# ==========================================================

if run and mode == "Manual Stock":

    if manual_symbol == "":

        st.warning("Please enter a stock symbol.")

    else:

        chart_placeholder.info(
            "Chart will be shown here.\n\n"
            "This will be connected in chart.py"
        )

# ==========================================================
# F&O
# ==========================================================

if run and mode == "F&O Stocks":

    #
    # Dummy dataframe
    # Will come from scanner.py
    #

    df = pd.DataFrame(
        {
            "Symbol": [
                "IRFC",
                "LT",
                "VBL",
                "ICICIBANK",
            ],
            "Trend": [
                "Down Trend",
                "Up Trend",
                "Up Trend",
                "Down Trend",
            ],
            "Candle": [
                "🔴",
                "🟢",
                "🟢",
                "🔴",
            ],
            "Trend Since": [
                "01-Jul-2026 15:15",
                "01-Jul-2026 15:00",
                "01-Jul-2026 15:15",
                "01-Jul-2026 15:15",
            ],
        }
    )

    progress_placeholder.empty()

    with results_placeholder.container():

        st.subheader("Results")

        h1, h2, h3, h4, h5 = st.columns(
            [2, 2, 1, 3, 1]
        )

        h1.markdown("**Symbol**")
        h2.markdown("**Trend**")
        h3.markdown("**Candle**")
        h4.markdown("**Trend Since**")
        h5.markdown("**Chart**")

        st.divider()

        for _, row in df.iterrows():

            c1, c2, c3, c4, c5 = st.columns(
                [2, 2, 1, 3, 1]
            )

            c1.write(row["Symbol"])
            c2.write(row["Trend"])
            c3.write(row["Candle"])
            c4.write(row["Trend Since"])

            if c5.button(
                "📈",
                key=row["Symbol"],
                use_container_width=True,
            ):

                chart_placeholder.info(
                    f"Chart for {row['Symbol']} "
                    "will appear here.\n\n"
                    "chart.py will handle this."
                )
