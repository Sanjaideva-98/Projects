import streamlit as st
import pandas as pd
from utils.api_handler import fetch_live_matches, fetch_match_details

def app():
    st.title("⚡ Live Match Updates")

    data = fetch_live_matches().get("matchList", [])
    if not data:
        st.warning("No live matches.")
        return

    titles = {
        f"{m['matchInfo']['seriesName']}: {m['matchInfo']['matchDesc']}": 
        m['matchInfo']['matchId']
        for m in data
    }
    choice = st.selectbox("Pick a match", list(titles.keys()))
    mid = titles[choice]
    det = fetch_match_details(mid)

    header = det.get("header", {}).get("matchHeader", {}).get("matchDesc", "")
    st.header(header)

    for t in det.get("scoreCard", {}).get("teamScores", []):
        st.subheader(t.get("inningsName", ""))
        if "batting" in t:
            st.dataframe(pd.DataFrame(t["batting"]), hide_index=True)
        if "bowling" in t:
            st.dataframe(pd.DataFrame(t["bowling"]), hide_index=True)
