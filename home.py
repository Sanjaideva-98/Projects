import streamlit as st
from utils.db_connection import run_query

def app():
    st.title("Welcome to the Cricket Analytics Dashboard 🏏")
    st.write("Your one-stop solution for cricket data analysis.")
    st.write("---")

    sql = """
      SELECT p.player_name, p.role, t.team_name
        FROM players p
        JOIN teams t ON t.team_id = p.team_id
       LIMIT 5;
    """
    try:
        df = run_query(sql)
        if df.empty:
            st.warning("No players in DB yet.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
