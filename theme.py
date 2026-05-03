import streamlit as st

def init_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

def toggle_theme():
    if st.session_state.theme == "dark":
        st.session_state.theme = "light"
    else:
        st.session_state.theme = "dark"

def apply_theme():
    if st.session_state.theme == "dark":
        st.markdown("""
        <style>
        body {background-color: #0f172a; color: white;}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        body {background-color: #f8fafc; color: black;}
        </style>
        """, unsafe_allow_html=True)