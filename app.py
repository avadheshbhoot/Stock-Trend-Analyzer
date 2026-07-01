"""
app.py
Streamlit UI for Stock Trend Analyzer
"""

import streamlit as st

from config import (
    DEFAULT_MA,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    DEFAULT_CHART_DAYS,
    SYMBOL_FILE,
)

from data_fetcher import load_symbols, save_results
from trend_analyzer import scan_market, analyze_stock
from charts import plot_chart


st.set_page_config(
    page_title="Stock Trend Analyzer",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Stock Trend Analyzer")

st.sidebar.header("Settings")

ma = st.sidebar.number_input(
    "Moving Average",
    min_value=5,
    max_value=500,
    value=DEFAULT_MA,
)

period = st.sidebar.selectbox(
    "Period",
    ["5D", "15D", "1mo", "3mo"],
    index=["5D", "15D", "1mo", "3mo"].index(DEFAULT_PERIOD),
)

interval = st.sidebar.selectbox(
    "Interval",
    ["15m", "30m", "60m"],
    index=["15m", "30m", "60m"].index(DEFAULT_INTERVAL),
)

mode = st.sidebar.radio(
    "Mode",
    [
        "Scan Market",
        "Analyze Stock",
    ],
)

if mode == "Scan Market":

    st.subheader("Market Scanner")

    if st.button("Scan Market"):

        tickers = load_symbols(SYMBOL_FILE)

        with st.spinner("Scanning market..."):

            results = scan_market(
                tickers=tickers,
                ma=ma,
                period=period,
                interval=interval,
            )

        st.success("Scan Completed")

        st.dataframe(
            results,
            use_container_width=True,
        )

        save_results(results, "Trend_Output.xlsx")

        with open("Trend_Output.xlsx", "rb") as f:

            st.download_button(
                "Download Excel",
                data=f,
                file_name="Trend_Output.xlsx",
            )

else:

    st.subheader("Single Stock Analysis")

    symbol = st.text_input(
        "Enter Yahoo Symbol",
        value="TCS.NS",
    )

    if st.button("Analyze"):

        with st.spinner("Analyzing..."):

            df, trend_date, candles = analyze_stock(
                ticker=symbol,
                ma=ma,
                period=period,
                interval=interval,
            )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Trend",
            df["safe_trend"].iloc[-1],
        )

        col2.metric(
            "Trend Started",
            trend_date.strftime("%d-%b-%Y %H:%M"),
        )

        col3.metric(
            "Candles",
            candles,
        )

        fig = plot_chart(
            df=df,
            ticker=symbol,
            ma=ma,
            days=DEFAULT_CHART_DAYS,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        st.dataframe(
            df.tail(20),
            use_container_width=True,
        )
