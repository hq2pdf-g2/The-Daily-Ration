"""
Railway Streamlit Demo
=======================

This is a demo project for deploying Streamlit apps on [Railway Platform](https://railway.com?referralCode=kanban).

Project Repository: https://github.com/markgzhou/railway-streamlit

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/SyDUOJ?referralCode=kanban)
"""

import streamlit as st

st.set_page_config(page_title="Railway Streamlit Demo", page_icon="🚄", layout="wide")

# Sidebar with project information and deployment link
with st.sidebar:
    st.header("📋 Project Info")
    st.markdown("**Public Repo:**")
    st.markdown(
        "[🔗 markgzhou/railway-streamlit](https://github.com/markgzhou/railway-streamlit)"
    )

    st.markdown("**Live Demo:**")
    st.markdown(
        "[🌐 streamlit-demo.up.railway.app](https://streamlit-demo.up.railway.app/)"
    )

    st.divider()

    st.header("🚀 Quick Deploy")
    st.markdown(
        "[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/SyDUOJ?referralCode=kanban)"
    )
    st.caption("Click the button above to deploy this app to Railway!")

st.title("Hello Streamlit from [Railway](https://railway.com?referralCode=kanban) 👋")
st.markdown(
    """ 
    This is a demo for you to try Streamlit on [Railway Platform](https://railway.com?referralCode=kanban) and have fun. 

    **There's :rainbow[so much] you can build!**
    
    We prepared a few examples for you to get started. Just 
    click on the buttons above and discover what you can do 
    with Streamlit. 
    """
)

if st.button("Send balloons!"):
    st.balloons()

st.markdown(
    """
    :rainbow[Find more information @ GitHub] [markgzhou/railway-streamlit](https://github.com/markgzhou/railway-streamlit)
    """
)
