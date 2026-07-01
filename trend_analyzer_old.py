"""
Trend Analysis Functions
"""

import numpy as np
import pandas as pd
import talib

from config import (
    RSI_PERIOD,
    ADX_PERIOD,
    RSI_UPTREND,
    RSI_DOWNTREND,
    ADX_THRESHOLD,
)

from data_fetcher import resample_ohlc


# ======================================================
# Indicator Calculation
# ======================================================

def calculate_indicators(df, ma):
    """
    Calculate EMA, RSI and ADX.
    """

    # 15 Minute EMA
    df[f"EMA_{ma}_15min"] = (
        df["Close"]
        .ewm(span=ma, adjust=False)
        .mean()
        .round(2)
    )

    # Higher Timeframes
    df45 = resample_ohlc(df, "45min")
    df90 = resample_ohlc(df, "90min")
    df180 = resample_ohlc(df, "180min")

    df45[f"EMA_{ma}_45min"] = (
        df45["Close"]
        .ewm(span=ma, adjust=False)
        .mean()
        .round(2)
    )

    df90[f"EMA_{ma}_90min"] = (
        df90["Close"]
        .ewm(span=ma, adjust=False)
        .mean()
        .round(2)
    )

    df180[f"EMA_{ma}_180min"] = (
        df180["Close"]
        .ewm(span=ma, adjust=False)
        .mean()
        .round(2)
    )

    # Merge EMA
    df = df.join(
        df45[[f"EMA_{ma}_45min"]],
        how="left",
    )

    df = df.join(
        df90[[f"EMA_{ma}_90min"]],
        how="left",
    )

    df = df.join(
        df180[[f"EMA_{ma}_180min"]],
        how="left",
    )

    # Fill Missing EMA
    ema_cols = [
        f"EMA_{ma}_15min",
        f"EMA_{ma}_45min",
        f"EMA_{ma}_90min",
        f"EMA_{ma}_180min",
    ]

    df[ema_cols] = df[ema_cols].ffill()

    # RSI
    df["RSI"] = talib.RSI(
        df["Close"],
        timeperiod=RSI_PERIOD,
    ).round(2)

    # ADX
    df["ADX"] = talib.ADX(
        df["High"],
        df["Low"],
        df["Close"],
        timeperiod=ADX_PERIOD,
    ).round(2)

    return df

# ======================================================
# Trend Calculation
# ======================================================

def calculate_trend(df, ma):
    """
    Calculate trend for every timeframe.
    """

    timeframes = [
        "15min",
        "45min",
        "90min",
        "180min",
    ]

    for tf in timeframes:

        ema = f"EMA_{ma}_{tf}"

        trend = f"{tf}_trend"

        df[trend] = np.where(
            df["Close"] >= df[ema],
            "up_trend",
            "down_trend",
        )

    # RSI + ADX

    df["rsi_n_adx_trend"] = "-"

    up = (
        (df["RSI"] >= RSI_UPTREND)
        &
        (df["ADX"] >= ADX_THRESHOLD)
    )

    down = (
        (df["RSI"] <= RSI_DOWNTREND)
        &
        (df["ADX"] <= ADX_THRESHOLD)
    )

    df.loc[
        up,
        "rsi_n_adx_trend",
    ] = "up_trend"

    df.loc[
        down,
        "rsi_n_adx_trend",
    ] = "down_trend"

    # Main Trend

    df["main_trend"] = np.where(

        (df["15min_trend"] == df["45min_trend"])
        &
        (df["45min_trend"] == df["90min_trend"])
        &
        (df["90min_trend"] == df["180min_trend"]),

        df["15min_trend"],

        "-"

    )

    # Safe Trend

    df["safe_trend"] = "-"

    condition = (

        (df["main_trend"] == df["main_trend"].shift(1))
        &
        (df["main_trend"].shift(1) == df["main_trend"].shift(2))
        &
        (df["main_trend"].shift(2) == df["main_trend"].shift(3))
        &
        (
            df["rsi_n_adx_trend"]
            ==
            df["rsi_n_adx_trend"].shift(1)
        )

    )

    df.loc[
        condition,
        "safe_trend",
    ] = df["main_trend"]

    return df

# ======================================================
# Trend Start
# ======================================================
def trend_start(df):
    """
    Return trend start datetime and
    number of candles.
    """

    last = df["safe_trend"].iloc[-1]

    count = 0

    for trend in reversed(df["safe_trend"]):

        if trend == last:

            count += 1

        else:

            break

    start_loc = len(df) - count

    return (
        df.index[start_loc],
        count,
    )