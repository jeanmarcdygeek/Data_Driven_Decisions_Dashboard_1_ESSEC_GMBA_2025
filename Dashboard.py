import streamlit as st
import pandas as pd
import json

COLS_TO_DISPLAY = [
        "Fund", "Manager", "Age", "Gender", 
        "Peer Ranking 1Y", "Peer Ranking 3Y", "Rating", "Fees", "ESG Label",
        "E Score", "AUM", "Type", "Sub Type", "Benchmark Name", "Start date"
    ]

st.set_page_config(layout="wide")


if not "funds_list" in st.session_state or not "nav_dfs" in st.session_state:
    fund_df = pd.read_excel("Funds List.xlsx")
    fund_df.rename(columns={
        "Renamed fund": "Fund",
        "Manager Name": "Manager",
        "Manager Age": "Age",
        "Manager Gender": "Gender",
        "Peer Ranking 1Y": "Peer Ranking 1Y",
        "Peer Ranking 3Y": "Peer Ranking 3Y",
        "Rating": "Rating",
        "Renamed Bench": "Benchmark Name",
        "Benchmark start date": "Start date",
    }, inplace=True)
    st.session_state["funds_list"] = fund_df
    st.session_state["nav_dfs"] = {}

    
    for i,row in fund_df.iterrows():
        file = str(row["File"])
        fund = str(row["Fund"])
        nav_file = f"./data/{file}"
        nav_df = pd.read_csv(nav_file)
        st.session_state["nav_dfs"][fund] = nav_df


st.title("Funds Dashboard")

st.dataframe(st.session_state["funds_list"][COLS_TO_DISPLAY])

st.markdown("### 📋 Disclaimer")
with st.expander("Metric Definitions and Notes", expanded=True):
    st.markdown("""
    **Rating:** Fund rating is on a scale of **5** (where 5 is the highest rating).
    
    **Peer Ranking:** Peer rankings are on a scale of **1 to 100**, where:
    - **1** represents the best performance (top performer)
    - **100** represents the worst performance (bottom performer)
    - Lower numbers indicate better relative performance
    
    **E Score (ESG Score):** The Environmental score is part of the ESG (Environmental, Social, Governance) rating.
    - **Lower scores are better** (indicating better environmental performance)
    - The score reflects the fund's environmental impact and practices
    """)