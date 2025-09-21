import streamlit as st
import pandas as pd
from utils.db_connection import get_db_connection

def app():
    st.title("🛠️ CRUD Operations")

    def add_player(name, team_id, role):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO players (player_name, team_id, role) VALUES (%s,%s,%s)"
        try:
            cursor.execute(sql, (name, team_id, role))
            conn.commit()
            st.success(f"Added player: {name}")
        except Exception as e:
            st.error(f"Failed to add: {e}")
        finally:
            conn.close()

    st.subheader("Add New Player")
    with st.form("add"):
        name = st.text_input("Name")
        team = st.number_input("Team ID", min_value=1)
        role = st.selectbox("Role", ["Batsman","Bowler","All-rounder","Wicket-keeper"])
        if st.form_submit_button("Add"):
            add_player(name, team, role)

    st.subheader("Current Players")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT player_id, player_name, role FROM players", conn)
    st.dataframe(df)
    conn.close()
