"""
ui.py

UI Components
"""

import streamlit as st
import pandas as pd


# ==========================================================
# Initialise Session State
# ==========================================================

def init_session():

    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = None

    if "scan_results" not in st.session_state:
        st.session_state.scan_results = pd.DataFrame()


# ==========================================================
# Display Scanner Results
# ==========================================================

def show_results(results: pd.DataFrame):

    if results.empty:
        st.info("No stocks found.")
        return

    df = results.copy()

    #
    # Selection Column
    #

    df.insert(0, "Select", False)

    #
    # Nice formatting
    #

    df["Trend"] = df["Trend"].replace(
        {
            "Up Trend": "🟢 Up",
            "Down Trend": "🔴 Down",
        }
    )

    st.subheader(f"Results ({len(df)})")

    edited_df = st.data_editor(

        df,

        hide_index=True,

        use_container_width=True,

        height=500,

        key="scanner_table",

        column_config={

            "Select": st.column_config.CheckboxColumn(

                width="small",

                help="Select stock"

            ),

            "Symbol": st.column_config.TextColumn(

                width="small"

            ),

            "Trend": st.column_config.TextColumn(

                width="medium"

            ),

            "Candle": st.column_config.TextColumn(

                width="small"

            ),

            "Trend Since": st.column_config.TextColumn(

                width="medium"

            ),

        },

        disabled=[

            "Symbol",

            "Trend",

            "Candle",

            "Trend Since",

        ],

    )

    #
    # Selected Row
    #

    selected = edited_df[edited_df["Select"]]

    if len(selected):

        symbol = selected.iloc[-1]["Symbol"]

        st.session_state.selected_symbol = symbol

    return st.session_state.selected_symbol
