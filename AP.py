import streamlit as st
import os

st.experimental_set_query_params(clear_cache=True)  # Forces Streamlit to refresh
# Debug: Confirm Streamlit is running
st.write("Hello! Streamlit app is running.")

# Debug: Print the current working directory
st.write("Current working directory:", os.getcwd())
