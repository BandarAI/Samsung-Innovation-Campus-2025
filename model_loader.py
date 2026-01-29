import os
import urllib.request
import streamlit as st
from ultralytics import YOLO

MODEL_NAME = "best.pt"
MODEL_URL = "https://huggingface.co/bandarai/food-reco-sic-2050/resolve/main/best.pt"

def download_model():
    """Download the YOLO model if it doesn't exist."""
    if not os.path.exists(MODEL_NAME):
        with st.spinner("📥 Downloading YOLO model... (first time only)"):
            urllib.request.urlretrieve(MODEL_URL, MODEL_NAME)

def load_model():
    """Load YOLO model (do NOT cache the model object)."""
    download_model()
    return YOLO(MODEL_NAME)
