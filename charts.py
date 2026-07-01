"""
chart.py

Draw candlestick charts.
"""

import streamlit as st
import plotly.graph_objects as go

from fetch_data import get_stock_data
from indicators import sma


# ==========================================================
# Build Figure
# ==========================================================

def build_chart(
    symbol: str,
    period: str,
    interval: str,
    ma_period: int,
):
    """
    Returns a Plotly Figure.
    """

    df = get_stock_data(
        ticker=symbol,
        period=period,
        interval=interval,
    )

    df = sma(
        df,
        ma_period,
    )

    ma_col = f"SMA_{ma_period}"

    fig = go.Figure()

    # ------------------------------------------------------
    # Candlestick
    # ------------------------------------------------------

    fig.add_trace(

        go.Candlestick(

            x=df.index,

            open=df["Open"],

            high=df["High"],

            low=df["Low"],

            close=df["Close"],

            name="Price",

        )

    )

    # ------------------------------------------------------
    # Moving Average
    # ------------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df[ma_col],

            mode="lines",

            name=f"MA {ma_period}",

            line=dict(
                width=2,
                color="orange",
            ),

        )

    )

    # ------------------------------------------------------
    # Layout
    # ------------------------------------------------------

    fig.update_layout(

        title=symbol,

        xaxis_title="",

        yaxis_title="Price",

        height=650,

        xaxis_rangeslider_visible=False,

        template="plotly_white",

        legend=dict(
            orientation="h",
        ),

    )

    return fig


# ==========================================================
# Show Chart
# ==========================================================

def show_chart(
    container,
    symbol: str,
    period: str,
    interval: str,
    ma_period: int,
):
    """
    Display chart inside any Streamlit container.
    """

    fig = build_chart(
        symbol,
        period,
        interval,
        ma_period,
    )

    with container:

        st.subheader(symbol)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )
