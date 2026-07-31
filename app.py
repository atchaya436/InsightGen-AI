"""
InsightGen AI: Automated Business Intelligence & Decision Support Platform
Module 1: Base application shell (title, description, sidebar, navigation)
"""

import streamlit as st
import pandas as pd

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
# SESSION STATE INITIALIZATION
# Streamlit reruns the whole script on every interaction, so we use
# session_state to persist the uploaded dataframe across reruns.
# We initialize it once, only if it doesn't already exist.
# -----------------------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None  # will hold the uploaded dataframe
if "filename" not in st.session_state:
    st.session_state.filename = None  # will hold the original file name

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

elif page == "📁 Upload Dataset":
    st.title("📁 Upload Dataset")
    st.markdown("Upload a **CSV** or **Excel (.xlsx)** file to get started.")

    # file_uploader returns None until the user actually uploads something.
    # type=[...] restricts which file extensions are selectable/droppable.
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
    )

    if uploaded_file is not None:
        try:
            # Read based on file extension.
            # uploaded_file.name gives us the original filename with extension.
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Store in session_state so other modules (cleaning, EDA, etc.)
            # can access this same dataframe without re-uploading.
            st.session_state.df = df
            st.session_state.filename = uploaded_file.name

            st.success(f"✅ Successfully loaded **{uploaded_file.name}**")

        except Exception as e:
            # Catch any read errors (corrupt file, wrong format, etc.)
            # instead of letting the app crash with a raw traceback.
            st.error(f"❌ Error reading file: {e}")

    # Only show preview + metadata if a dataframe currently exists in session_state
    if st.session_state.df is not None:
        df = st.session_state.df

        st.markdown("---")
        st.subheader("📋 Dataset Preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("---")
        st.subheader("📊 Dataset Overview")

        # st.columns lets us lay out metric cards side by side
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Rows", f"{df.shape[0]:,}")
        with col2:
            st.metric("Columns", f"{df.shape[1]:,}")
        with col3:
            total_nulls = int(df.isnull().sum().sum())
            st.metric("Total Null Values", f"{total_nulls:,}")
        with col4:
            # memory_usage(deep=True) accounts for actual memory used by
            # object/string columns too, not just numeric ones.
            memory_bytes = df.memory_usage(deep=True).sum()
            memory_mb = memory_bytes / (1024 ** 2)
            st.metric("Memory Usage", f"{memory_mb:.2f} MB")

        st.markdown("---")
        st.subheader("🔎 Column Details")

        # Build a summary table: one row per column, showing dtype,
        # null count, and unique value count — very useful at a glance.
        column_summary = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Null Values": df.isnull().sum().values,
            "Unique Values": df.nunique().values,
        })

        st.dataframe(column_summary, use_container_width=True, hide_index=True)

    else:
        st.info("👆 Upload a file above to see the dataset preview and summary.")

else:
    # Placeholder for all remaining not-yet-built pages
    st.title(page)
    st.warning(f"🚧 The **{page}** module hasn't been built yet. Coming in a future step!")