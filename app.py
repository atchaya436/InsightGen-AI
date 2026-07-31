"""
InsightGen AI: Automated Business Intelligence & Decision Support Platform
Module 1: Base application shell (title, description, sidebar, navigation)
"""

import streamlit as st

# -----------------------------------------------------------------------
# PAGE CONFIGURATION
# Must be the FIRST Streamlit command in the script.
# Sets the browser tab title, icon, and overall page layout.
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="InsightGen AI",
    page_icon="📊",
    layout="wide",              # uses full browser width instead of a centered narrow column
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------
# SIDEBAR — NAVIGATION MENU
# st.sidebar places widgets in the fixed left panel, separate from
# the main page content.
# -----------------------------------------------------------------------
st.sidebar.title("📊 InsightGen AI")
st.sidebar.markdown("---")  # horizontal divider line

# radio button acting as our navigation menu for now.
# Later modules will each become one of these options.
page = st.sidebar.radio(
    "Navigate",
    options=[
        "🏠 Home",
        "📁 Upload Dataset",
        "🧹 Data Cleaning",
        "📈 EDA",
        "📌 KPIs",
        "📊 Dashboard",
        "💡 Insights",
        "✅ Recommendations",
        "📤 Reports",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Python & Streamlit")

# -----------------------------------------------------------------------
# MAIN PAGE CONTENT
# For now, only the "Home" option shows real content.
# Every other option shows a placeholder message — we'll build
# each of these out module by module.
# -----------------------------------------------------------------------
if page == "🏠 Home":
    st.title("📊 InsightGen AI")
    st.subheader("Automated Business Intelligence & Decision Support Platform")

    st.markdown(
        """
        Welcome to **InsightGen AI** — an end-to-end platform that turns any raw
        CSV or Excel dataset into a fully automated business intelligence report.

        **What this app will do:**
        - 🧹 Automatically clean and prepare your dataset
        - 📈 Generate exploratory data analysis (EDA)
        - 📌 Calculate relevant business KPIs
        - 📊 Build an interactive dashboard
        - 💡 Surface plain-English business insights
        - ✅ Recommend data-driven next steps
        - 📤 Export a full report

        Use the sidebar on the left to navigate between sections as they're built.
        """
    )

    st.info("👈 This is currently a skeleton app. Each section will be built module by module.")

else:
    # Placeholder for all not-yet-built pages
    st.title(page)
    st.warning(f"🚧 The **{page}** module hasn't been built yet. Coming in a future step!")