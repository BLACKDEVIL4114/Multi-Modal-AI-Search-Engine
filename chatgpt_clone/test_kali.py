import streamlit as st
st.set_page_config(page_title="Kali Test", layout="wide")
st.title("✦ KALI SYSTEM TEST")
st.success("If you see this, the server is healthy.")
if st.button("Test Logic"):
    st.write("Logic verified.")
