import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide")
st.title("WFU Soccer – Coach Dashboard")

# -----------------------------------
# SIMPLE EXCEL LOAD (same folder)
# -----------------------------------
sheets = pd.read_excel(
    "./WFU_SoccerTeam_Report.xlsx",
    sheet_name=None,
    header=2
)

# Pull sheets
match_summary = sheets.get("Match Summary (Analyst Data)")
coach_view = sheets.get("Dashboard (Coach View)")
targets_notes = sheets.get("Targets & Notes")

# -----------------------------------
# Sidebar
# -----------------------------------
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select View",
    ["Coach Overview", "Compare Two Games", "Trends", "All Sheets"]
)

# -----------------------------------
# COACH OVERVIEW
# -----------------------------------
if page == "Coach Overview":
    st.header("Coach Overview")

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("Season KPIs")
        if coach_view is not None:
            st.dataframe(coach_view, use_container_width=True)
        else:
            st.warning("Dashboard (Coach View) sheet not found")

    with col2:
        st.subheader("Targets & Notes")
        if targets_notes is not None:
            st.dataframe(targets_notes, use_container_width=True)
        else:
            st.warning("Targets & Notes sheet not found")

# -----------------------------------
# COMPARE TWO GAMES
# -----------------------------------
elif page == "Compare Two Games":
    st.header("Compare Two Games")

    if match_summary is None:
        st.warning("Match Summary sheet not found")
        st.stop()

    df = match_summary.copy()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Game_Label"] = (
        df["Date"].dt.strftime("%Y-%m-%d").fillna("Unknown Date")
        + " vs " + df["Opponent"].astype(str)
        + " (" + df["Result"].astype(str) + ")"
    )

    games = df["Game_Label"].tolist()

    col1, col2 = st.columns(2)
    with col1:
        g1 = st.selectbox("Game 1", games, index=0)
    with col2:
        g2 = st.selectbox("Game 2", games, index=1)

    r1 = df[df["Game_Label"] == g1].iloc[0]
    r2 = df[df["Game_Label"] == g2].iloc[0]

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    metrics = st.multiselect(
        "Select metrics to compare",
        numeric_cols,
        default=numeric_cols[:6]
    )

    comp = pd.DataFrame({
        "Metric": metrics,
        "Game 1": [r1[m] for m in metrics],
        "Game 2": [r2[m] for m in metrics],
        "Difference (Game2 - Game1)": [r2[m] - r1[m] for m in metrics]
    })

    st.dataframe(comp, use_container_width=True)

# -----------------------------------
# TRENDS
# -----------------------------------
elif page == "Trends":
    st.header("Trends Over Time")

    if match_summary is None:
        st.warning("Match Summary sheet not found")
        st.stop()

    df = match_summary.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    metric = st.selectbox("Select metric", numeric_cols)

    fig = px.line(
        df,
        x="Date",
        y=metric,
        markers=True,
        title=f"{metric} Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# RAW SHEETS
# -----------------------------------
else:
    st.header("All Sheets (Raw Data)")
    sheet_name = st.selectbox("Select a sheet", list(sheets.keys()))
    st.dataframe(sheets[sheet_name], use_container_width=True)