import streamlit as st


def inject_global_css():
    st.markdown(
        """
        <style>
        /* ---------- GLOBAL ---------- */
        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", sans-serif;
        }

        /* ---------- PAGE ---------- */
        .main {
            padding: 2rem;
        }

        /* ---------- HEADINGS ---------- */
        h1 {
            font-weight: 700;
            color: #1f2937;
        }

        h2, h3 {
            color: #374151;
        }

        /* ---------- CARDS ---------- */
        .card {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        }

        /* ---------- BUTTONS ---------- */
        button[kind="primary"] {
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600;
        }

        /* ---------- INPUTS ---------- */
        input, textarea {
            border-radius: 8px !important;
        }

        /* ---------- ALERTS ---------- */
        .stAlert {
            border-radius: 10px;
        }

        /* ---------- FOOTER ---------- */
        footer {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
