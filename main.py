import os
import sys
import streamlit as st
from pathlib import Path
import page1,page2
from streamlit_option_menu import option_menu
from base64 import b64encode


st.set_page_config(
    page_title="Capstone SIC 2025",
    layout="wide"
)


class MultiApp:
    def __init__(self):
        self.apps = []
        
    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })
        
    def run():
        
        try:
            with open('logo_.jpg', 'rb') as img_f:
                img_bytes = img_f.read()
            encoded = b64encode(img_bytes).decode()
            img_html = f"<div style='text-align:center'><img src='data:image/jpeg;base64,{encoded}' width='220' /></div>"
            st.sidebar.markdown(img_html, unsafe_allow_html=True)
        except Exception:
            st.sidebar.image('logo_.jpg', width=220)

        st.sidebar.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        with st.sidebar:
            app = option_menu(
                "",
                options=['IMAGE', 'VIDEO'],
                icons=['cloud-upload-fill', 'compass-fill', 'binoculars-fill'],
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": '#ff6666'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "black"},
                },
            )

        st.sidebar.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if app == "IMAGE":
            page1.app()
        if app == "VIDEO":
            page2.app()

        footer_html = """
        <div style='text-align:center; font-size:11px; color:#ffffff; padding-top:6px;'>
          <div style='margin-bottom:8px; font-size:20px;'><strong>📦 Repository 📦</strong></div>
          <div style='margin-bottom:10px;'><a href='https://github.com/BandarAI/Samsung-Innovation-Campus-2025' target='_blank' style='color:#ffffff; text-decoration:none; font-size:15px;'>SIC Capstone 2025</a></div>
          <div style='margin-bottom:6px; font-size:20px;'><strong>🛠️ Developers 🛠️</strong></div>
          <div style='line-height:1.6; font-size:13px;'>
            <a href='https://github.com/BandarAI' target='_blank' style='color:#ffffff; text-decoration:none;'>BandarAI</a>&nbsp;|&nbsp;
            <a href='https://github.com/m7mdxyz' target='_blank' style='color:#ffffff; text-decoration:none;'>m7mdxyz</a>&nbsp;|&nbsp;
            <a href='https://github.com/AmjadJK' target='_blank' style='color:#ffffff; text-decoration:none;'>AmjadJK</a>&nbsp;|&nbsp;
            <a href='https://github.com/CsAbdulmalik' target='_blank' style='color:#ffffff; text-decoration:none;'>CsAbdulmalik</a>
          </div>
        </div>
        """
        st.sidebar.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.sidebar.markdown(footer_html, unsafe_allow_html=True)
    run()