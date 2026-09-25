
import streamlit as st

def money(v):
    sign = "-" if v < 0 else ""
    return f"{sign}₹{abs(v):,.0f} Cr"

def apply_style():
    st.markdown("""
    <style>
    .block-container{padding-top:1.2rem;max-width:1450px}
    .hero{padding:1.2rem 1.4rem;border-radius:16px;background:linear-gradient(135deg,#102a43,#176b87);color:white;margin-bottom:1rem}
    .hero h1{margin:0;font-size:2rem}.hero p{margin:.35rem 0 0;opacity:.88}
    .kpi{padding:1rem;border:1px solid #dfe7ef;border-radius:14px;background:white;box-shadow:0 2px 10px rgba(0,0,0,.04)}
    .kpi .label{font-size:.82rem;color:#667085}.kpi .value{font-size:1.7rem;font-weight:750;color:#102a43}
    .alert{padding:1rem;border-radius:12px;border-left:5px solid #cbd5e1;background:#f8fafc;margin:.5rem 0}
    .alert.high{border-left-color:#dc2626}.alert.medium{border-left-color:#f59e0b}.alert.low{border-left-color:#16a34a}
    .small{font-size:.82rem;color:#667085}
    </style>
    """, unsafe_allow_html=True)
