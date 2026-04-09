import streamlit as st

# 1. Setup Global Styles
def inject_global_css():
    st.markdown(
        """
        <style>
        h1, h2, h3, h4, h5, h6, 
        [data-testid="stMarkdownContainer"] h1, 
        [data-testid="stMarkdownContainer"] h2, 
        [data-testid="stMarkdownContainer"] h3 {
            color: #2c3e50 ;
            background: none ;
        }
        .card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        footer, header { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True
    )