"""
safe_trend.py

Safe Trend Detection
"""

import numpy as np
import pandas as pd

from indicators import ema
from indicators import rsi
from indicators import adx


# ==========================================================
# Multi Timeframe EMA
# ==========================================================

def prepare_timeframes(
    df: pd.DataFrame,
    ma: int,
):

    frames = {}

    for tf in [45, 90, 180]:

        tf_df = (
            df.resample(f"{tf}min")
            .agg(
                {
                    "Open": "first",
                    "High": "max",
                    "Low": "min",
                    "Close": "last",
                }
            )
            .dropna()
        )

        tf_df = ema(
            tf_df,
            ma,
            column="Close",
        )

        frames[tf] = tf_df

    return frames


# ==========================================================
# Merge EMA
# ==========================================================

def merge_timeframes(
    df,
    frames,
    ma,
):

    df = ema(df, ma)

    for tf in [45, 90, 180]:

        col = f"EMA_{ma}"

        df = df.join(

            frames[tf][[col]].rename(

                columns={

                    col: f"EMA_{ma}_{tf}"

                }

            ),

            how="left",

        )

        df[f"EMA_{ma}_{tf}"] = (

            df[f"EMA_{ma}_{tf}"]

            .ffill()

        )

    return df


# ==========================================================
# Trend Columns
# ==========================================================

def create_trend_columns(
    df,
    ma,
):

    df["15min_trend"] = np.where(

        df["Close"] >= df[f"EMA_{ma}"],

        "up_trend",

        "down_trend",

    )

    for tf in [45, 90, 180]:

        df[f"{tf}min_trend"] = np.where(

            df["Close"] >= df[f"EMA_{ma}_{tf}"],

            "up_trend",

            "down_trend",

        )

    return df


# ==========================================================
# Main Trend
# ==========================================================

def calculate_main_trend(df):

    df["main_trend"] = np.where(

        (

            (df["15min_trend"] == df["45min_trend"])

            &

            (df["45min_trend"] == df["90min_trend"])

            &

            (df["90min_trend"] == df["180min_trend"])

        ),

        df["15min_trend"],

        "-",

    )

    return df


# ==========================================================
# RSI + ADX Filter
# ==========================================================

def apply_strength_filter(df):

    df = rsi(df)

    df = adx(df)

    df["rsi_n_adx_trend"] = "-"

    df.loc[

        (df.RSI >= 50)

        &

        (df.ADX >= 40),

        "rsi_n_adx_trend",

    ] = "up_trend"

    df.loc[

        (df.RSI <= 55)

        &

        (df.ADX <= 40),

        "rsi_n_adx_trend",

    ] = "down_trend"

    return df


# ==========================================================
# Safe Trend
# ==========================================================

def calculate_safe_trend(df):

    df["safe_trend"] = df["main_trend"].where(

        (

            df["main_trend"]

            ==

            df["main_trend"].shift()

        )

        &

        (

            df["main_trend"]

            ==

            df["main_trend"].shift(2)

        )

        &

        (

            df["main_trend"]

            ==

            df["main_trend"].shift(3)

        )

        &

        (

            df["rsi_n_adx_trend"]

            ==

            df["rsi_n_adx_trend"].shift()

        ),

        "-",

    )

    return df


# ==========================================================
# Trend Start
# ==========================================================

def trend_start(df):

    last = df["safe_trend"].iloc[-1]

    count = 0

    for value in reversed(df["safe_trend"]):

        if value == last:

            count += 1

        else:

            break

    idx = len(df) - count

    return {

        "last_safe_trend": last,

        "safe_trend_start_index": df.index[idx],

        "safe_trend_start_date": df.index[idx].date(),

    }


# ==========================================================
# Master Function
# ==========================================================

def safe_trend(df, ma):

    frames = prepare_timeframes(df, ma)

    df = merge_timeframes(df, frames, ma)

    df = create_trend_columns(df, ma)

    df = apply_strength_filter(df)

    df = calculate_main_trend(df)

    df = calculate_safe_trend(df)

    summary = trend_start(df)

    return df, summary
