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
    st.session_state.df = None  # will hold the original uploaded dataframe
if "filename" not in st.session_state:
    st.session_state.filename = None  # will hold the original file name
if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None  # will hold the cleaned dataframe

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

elif page == "🧹 Data Cleaning":
    st.title("🧹 Data Cleaning")

    if st.session_state.df is None:
        st.info("👆 Please upload a dataset first on the **Upload Dataset** page.")
    else:
        # Start cleaning from the original df each time this page loads,
        # unless we already have a cleaned version in progress.
        if st.session_state.cleaned_df is None:
            st.session_state.cleaned_df = st.session_state.df.copy()

        df = st.session_state.cleaned_df

        # -----------------------------------------------------------
        # DUPLICATE DETECTION & REMOVAL
        # -----------------------------------------------------------
        st.subheader("🔁 Duplicate Rows")

        duplicate_count = int(df.duplicated().sum())

        col1, col2 = st.columns([3, 1])
        with col1:
            if duplicate_count > 0:
                st.warning(f"Found **{duplicate_count}** duplicate row(s).")
            else:
                st.success("No duplicate rows found.")
        with col2:
            # disabled=... prevents clicking the button when there's nothing to do
            if st.button("Remove Duplicates", disabled=(duplicate_count == 0)):
                # keep='first' keeps the first occurrence, drops the rest
                df = df.drop_duplicates(keep="first").reset_index(drop=True)
                st.session_state.cleaned_df = df
                st.success(f"Removed {duplicate_count} duplicate row(s).")
                st.rerun()  # re-run the script so the UI reflects the updated data immediately

        st.markdown("---")

        # -----------------------------------------------------------
        # MISSING VALUE DETECTION & HANDLING
        # -----------------------------------------------------------
        st.subheader("❓ Missing Values")

        null_counts = df.isnull().sum()
        null_counts = null_counts[null_counts > 0]  # only show columns that actually have nulls

        if null_counts.empty:
            st.success("No missing values found.")
        else:
            st.warning(f"Found missing values in **{len(null_counts)}** column(s):")

            null_summary = pd.DataFrame({
                "Column": null_counts.index,
                "Missing Count": null_counts.values,
                "Missing %": (null_counts.values / len(df) * 100).round(2),
            })
            st.dataframe(null_summary, use_container_width=True, hide_index=True)

            strategy = st.selectbox(
                "Choose a strategy to handle missing values:",
                options=[
                    "Drop rows with any missing values",
                    "Fill numeric columns with median, categorical with mode",
                    "Fill numeric columns with mean, categorical with mode",
                    "Fill all missing values with a constant",
                ],
            )

            fill_constant = None
            if strategy == "Fill all missing values with a constant":
                fill_constant = st.text_input("Enter the constant value to use:", value="Unknown")

            if st.button("Apply Missing Value Strategy"):
                if strategy == "Drop rows with any missing values":
                    df = df.dropna().reset_index(drop=True)

                elif strategy == "Fill numeric columns with median, categorical with mode":
                    for col in df.columns:
                        if df[col].isnull().sum() == 0:
                            continue
                        if pd.api.types.is_numeric_dtype(df[col]):
                            df[col] = df[col].fillna(df[col].median())
                        else:
                            # mode() can return multiple values if tied; take the first
                            mode_val = df[col].mode(dropna=True)
                            if not mode_val.empty:
                                df[col] = df[col].fillna(mode_val[0])

                elif strategy == "Fill numeric columns with mean, categorical with mode":
                    for col in df.columns:
                        if df[col].isnull().sum() == 0:
                            continue
                        if pd.api.types.is_numeric_dtype(df[col]):
                            df[col] = df[col].fillna(df[col].mean())
                        else:
                            mode_val = df[col].mode(dropna=True)
                            if not mode_val.empty:
                                df[col] = df[col].fillna(mode_val[0])

                elif strategy == "Fill all missing values with a constant":
                    df = df.fillna(fill_constant)

                st.session_state.cleaned_df = df
                st.success("Missing value strategy applied.")
                st.rerun()

        st.markdown("---")
        st.subheader("📋 Current Cleaned Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Current shape: {df.shape[0]} rows × {df.shape[1]} columns")

else:
    # Placeholder for all remaining not-yet-built pages
    st.title(page)
    st.warning(f"🚧 The **{page}** module hasn't been built yet. Coming in a future step!")