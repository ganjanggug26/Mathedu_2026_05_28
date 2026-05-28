import html
import math
from dataclasses import dataclass

import streamlit as st
from streamlit.components.v1 import html as st_html


st.set_page_config(
    page_title="미적분I: 속도와 가속도 시각화",
    page_icon=".",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
    .block-container {
        max-width: 1280px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.35rem;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 760;
        margin: 0.4rem 0 0.1rem;
    }
    .subtle {
        color: #5d6673;
        font-size: 0.95rem;
        line-height: 1.45;
    }
    .formula-box {
        border: 1px solid #d8dee8;
        background: #f7f9fc;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.35rem;
        font-family: "KaTeX_Main", "Computer Modern Serif", "CMU Serif", "Latin Modern Roman", "Times New Roman", serif;
        font-size: 1.12rem;
    }
    .formula-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.5rem 0 1rem;
    }
    .formula-card {
        border: 1px solid #d8dee8;
        background: #ffffff;
        border-radius: 8px;
        padding: 0.95rem 1rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }
    .formula-card .label {
        color: #475467;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 0.86rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }
    .formula-card .math {
        color: #111827;
        font-family: "KaTeX_Main", "Computer Modern Serif", "CMU Serif", "Latin Modern Roman", "Times New Roman", serif;
        font-size: 1.35rem;
        font-weight: 700;
        line-height: 1.35;
    }
    .detail-card {
        border: 1px solid #d8dee8;
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.95rem 1rem;
        min-height: 8.8rem;
    }
    .detail-card h4 {
        margin: 0 0 0.55rem;
        font-size: 1rem;
    }
    .detail-card p {
        margin: 0.38rem 0;
        font-size: 1.03rem;
    }
    .math-text {
        font-family: "KaTeX_Main", "Computer Modern Serif", "CMU Serif", "Latin Modern Roman", "Times New Roman", serif;
        font-size: 1.08rem;
        font-weight: 700;
    }
    @media (max-width: 860px) {
        .formula-grid {
            grid-template-columns: 1fr;
        }
    }
    .stButton > button {
        min-height: 2.7rem;
        border-radius: 8px;