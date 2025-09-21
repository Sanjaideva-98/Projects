import streamlit as st
import traceback

st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")

st.sidebar.title("📊 Cricbuzz LiveStats")
choice = st.sidebar.radio(
    "Go to",
    ["Home", "CRUD Operations", "Live Updates", "SQL Analytics"],
)

def _load_page(module_path: str, func_name: str = "app"):
    try:
        module = __import__(module_path, fromlist=[func_name])
        return getattr(module, func_name)
    except Exception:
        def _err():
            st.error(f"Failed to load `{module_path}`")
            st.code(traceback.format_exc())
        return _err

if choice == "Home":
    render = _load_page("pages.home")
elif choice == "CRUD Operations":
    render = _load_page("pages.crud_operations")
elif choice == "Live Updates":
    render = _load_page("pages.live_match_updates")
else:
    render = _load_page("pages.sql_analytics")

render()
