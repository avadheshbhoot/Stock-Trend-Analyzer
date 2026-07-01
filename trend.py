"""
trend.py

Trend Detection Functions
"""

import pandas as pd


# ==========================================================
# Current Trend
# ==========================================================

def current_trend(
    df: pd.DataFrame,
    ma_period: int,
):
    """
    Returns

    Up Trend
    Down Trend
    """

    ma_col = f"SMA_{ma_period}"

    if df.iloc[-1]["Close"] >= df.iloc[-1][ma_col]:

        return "Up Trend"

    return "Down Trend"


# ==========================================================
# Candle Color
# ==========================================================

def candle_color(
    df: pd.DataFrame,
):
    """
    Returns

    🟢
    🔴
    """

    last = df.iloc[-1]

    if last["Close"] >= last["Open"]:

        return "🟢"

    return "🔴"


# ==========================================================
# Trend Since
# ==========================================================

def trend_since(
    df: pd.DataFrame,
    ma_period: int,
):
    """
    Returns the datetime when
    current trend started.
    """

    ma_col = f"SMA_{ma_period}"

    current = current_trend(
        df,
        ma_period,
    )

    for i in range(len(df) - 2, -1, -1):

        close = df.iloc[i]["Close"]

        ma = df.iloc[i][ma_col]

        trend = (

            "Up Trend"

            if close >= ma

            else "Down Trend"

        )

        if trend != current:

            return df.index[i + 1]

    return df.index[0]


# ==========================================================
# Trend Summary
# ==========================================================

def trend_summary(
    df: pd.DataFrame,
    ma_period: int,
):
    """
    Returns dictionary used
    by scanner.py
    """

    trend = current_trend(
        df,
        ma_period,
    )

    since = trend_since(
        df,
        ma_period,
    )

    return {

        "Trend": trend,

        "Candle": candle_color(df),

        "Trend Since": since.strftime(
            "%d-%b-%Y %H:%M"
        )

    }
