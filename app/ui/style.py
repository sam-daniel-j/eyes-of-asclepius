import streamlit as st


def inject_global_css():
    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL (DO NOT OVERRIDE THEME BACKGROUND)
        ================================================== */

        html, body, .stApp,
        section[data-testid="stAppViewContainer"],
        section[data-testid="stMain"],
        .block-container {
            background: transparent;
        }

        .block-container {
            padding-top: 1.5rem;
        }

        /* ==================================================
           CARDS (ORIGINAL STYLE)
        ================================================== */

        .card {
            background: var(--secondary-background-color);
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid rgba(0,0,0,0.08);
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        }

        /* ==================================================
           HEADINGS
        ================================================== */

        h1 {
            font-weight: 700;
        }

        h2, h3 {
            opacity: 0.9;
        }

        /* ==================================================
           BUTTONS
        ================================================== */

        button[kind="primary"] {
            border-radius: 8px !important;
            font-weight: 600;
        }

        /* ==================================================
           INPUTS
        ================================================== */

        input, textarea, select {
            border-radius: 8px !important;
        }

        /* ==================================================
           ALERTS
        ================================================== */

        .stAlert {
            border-radius: 10px;
        }

        /* ==================================================
           SIDEBAR (MINIMAL)
        ================================================== */

        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(0,0,0,0.08);
        }

        /* ==================================================
           CLEANUP
        ================================================== */

        footer {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
