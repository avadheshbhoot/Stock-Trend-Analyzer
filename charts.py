"""
charts.py
Chart utilities for Stock Trend Analyzer.
Uses Plotly so charts work seamlessly in Streamlit.
"""

import plotly.graph_objects as go


def plot_chart(df, ticker: str, ma: int, days: int = 4):
    """
    Returns a Plotly figure.
    """

    last_date = df.index.max()
    df = df[df.index >= (last_date - df.index.to_series().diff().median() * 0)]  # keep index type
    cutoff = last_date - __import__("pandas").Timedelta(days=days)
    df = df[df.index >= cutoff]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            name="Close",
            line=dict(width=3),
        )
    )

    colors = {
        "15min": "#1f77b4",
        "45min": "#ff7f0e",
        "90min": "#2ca02c",
        "180min": "#d62728",
    }

    for tf in ["15min", "45min", "90min", "180min"]:
        col = f"EMA_{ma}_{tf}"
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=col,
                    line=dict(width=1, color=colors[tf]),
                )
            )

    current_trend = df["safe_trend"].iloc[-1] if "safe_trend" in df.columns else "-"

    fig.update_layout(
        title=f"{ticker} | Current Trend: {current_trend}",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
        legend_title="Indicators",
        height=650,
    )

    return fig
