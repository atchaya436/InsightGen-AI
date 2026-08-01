"""
InsightGen AI: Automated Business Intelligence & Decision Support Platform
Module 1: Base application shell (title, description, sidebar, navigation)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
import plotly.express as px
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


        st.markdown("---")

        # -----------------------------------------------------------
        # OUTLIER DETECTION & TREATMENT (IQR METHOD)
        # -----------------------------------------------------------
        st.subheader("📉 Outlier Detection (IQR Method)")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if not numeric_cols:
            st.info("No numeric columns available for outlier detection.")
        else:
            selected_outlier_cols = st.multiselect(
                "Select numeric columns to check for outliers:",
                options=numeric_cols,
                default=numeric_cols,
            )

            outlier_summary_rows = []
            outlier_bounds = {}

            for col in selected_outlier_cols:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_count = int(outlier_mask.sum())

                outlier_bounds[col] = (lower_bound, upper_bound)
                outlier_summary_rows.append({
                    "Column": col,
                    "Outliers Found": outlier_count,
                    "Lower Bound": round(lower_bound, 2),
                    "Upper Bound": round(upper_bound, 2),
                })

            outlier_summary_df = pd.DataFrame(outlier_summary_rows)
            st.dataframe(outlier_summary_df, use_container_width=True, hide_index=True)

            total_outliers = outlier_summary_df["Outliers Found"].sum()

            if total_outliers == 0:
                st.success("No outliers detected in the selected columns.")
            else:
                treatment = st.radio(
                    "How should outliers be treated?",
                    options=["Cap outliers to the IQR boundary", "Remove rows containing outliers"],
                    horizontal=True,
                )

                if st.button("Apply Outlier Treatment"):
                    if treatment == "Cap outliers to the IQR boundary":
                        for col, (lower_bound, upper_bound) in outlier_bounds.items():
                            # .clip() pulls any value below lower_bound up to lower_bound,
                            # and any value above upper_bound down to upper_bound.
                            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                        st.session_state.cleaned_df = df
                        st.success("Outliers capped to IQR boundaries.")

                    else:  # Remove rows containing outliers
                        combined_mask = pd.Series(False, index=df.index)
                        for col, (lower_bound, upper_bound) in outlier_bounds.items():
                            combined_mask |= (df[col] < lower_bound) | (df[col] > upper_bound)
                        df = df[~combined_mask].reset_index(drop=True)
                        st.session_state.cleaned_df = df
                        st.success(f"Removed {int(combined_mask.sum())} row(s) containing outliers.")

                    

        st.markdown("---")

        # -----------------------------------------------------------
        # DATA TYPE CORRECTION
        # -----------------------------------------------------------
        st.subheader("🔧 Data Type Correction")
        st.caption("Attempts to convert text columns that actually contain numbers into proper numeric columns.")

        if st.button("Auto-Correct Numeric Columns"):
            converted_cols = []
            for col in df.columns:
                if df[col].dtype == "object":
                    # errors="coerce" turns anything unconvertible into NaN
                    # instead of raising an exception.
                    converted = pd.to_numeric(df[col], errors="coerce")
                    # Only apply the conversion if MOST values converted successfully
                    # (otherwise we'd be wrongly numeric-ifying a genuine text column).
                    non_null_original = df[col].notna().sum()
                    non_null_converted = converted.notna().sum()
                    if non_null_original > 0 and (non_null_converted / non_null_original) > 0.9:
                        df[col] = converted
                        converted_cols.append(col)

            st.session_state.cleaned_df = df
            if converted_cols:
                st.success(f"Converted to numeric: {', '.join(converted_cols)}")
            else:
                st.info("No columns needed numeric conversion.")
            

        st.markdown("---")

        # -----------------------------------------------------------
        # DATE PARSING
        # -----------------------------------------------------------
        st.subheader("📅 Date Parsing")
        st.caption("Scans column names for date-like keywords and attempts to parse them as dates.")

        date_keywords = ["date", "time", "dob", "day", "month", "year"]
        candidate_date_cols = [
            col for col in df.columns
            if any(keyword in col.lower() for keyword in date_keywords)
        ]

        if not candidate_date_cols:
            st.info("No date-like column names detected.")
        else:
            st.write(f"Detected possible date columns: {', '.join(candidate_date_cols)}")
            if st.button("Parse Detected Date Columns"):
                parsed_cols = []
                for col in candidate_date_cols:
                    try:
                        # errors="coerce" turns unparseable dates into NaT (Not a Time)
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                        parsed_cols.append(col)
                    except Exception:
                        pass
                st.session_state.cleaned_df = df
                st.success(f"Parsed as dates: {', '.join(parsed_cols)}")
               

        st.markdown("---")

        # -----------------------------------------------------------
        # COLUMN RENAMING (STANDARDIZATION)
        # -----------------------------------------------------------
        st.subheader("🏷️ Standardize Column Names")
        st.caption("Converts column names to lowercase with underscores (e.g., 'Annual Income (k$)' → 'annual_income_k').")

        if st.button("Standardize Column Names"):
            new_columns = {}
            for col in df.columns:
                new_col = col.strip().lower()
                new_col = new_col.replace(" ", "_")
                # Remove any character that isn't a letter, number, or underscore
                new_col = "".join(ch for ch in new_col if ch.isalnum() or ch == "_")
                # Collapse multiple consecutive underscores into one
                while "__" in new_col:
                    new_col = new_col.replace("__", "_")
                new_col = new_col.strip("_")
                new_columns[col] = new_col

            df = df.rename(columns=new_columns)
            st.session_state.cleaned_df = df
            st.success("Column names standardized.")
            

        st.markdown("---")
        st.subheader("📋 Current Cleaned Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Current shape: {df.shape[0]} rows × {df.shape[1]} columns")

        # -----------------------------------------------------------
        # DOWNLOAD CLEANED DATASET
        # -----------------------------------------------------------
        st.markdown("---")
        st.subheader("⬇️ Download Cleaned Dataset")

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Cleaned Data as CSV",
            data=csv_data,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
        )
        st.download_button(
            label="Download Cleaned Data as CSV",
            data=csv_data,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
        )

elif page == "📈 EDA":
    st.title("📈 Exploratory Data Analysis (EDA)")

    # EDA should run on the cleaned dataset if available, otherwise fall
    # back to the raw uploaded dataset so the page still works even if
    # the user skipped the cleaning step.
    if st.session_state.cleaned_df is not None:
        df = st.session_state.cleaned_df
        st.caption("Using the cleaned dataset from the Data Cleaning step.")
    elif st.session_state.df is not None:
        df = st.session_state.df
        st.caption("Using the original uploaded dataset (no cleaning applied yet).")
    else:
        df = None

    if df is None:
        st.info("👆 Please upload a dataset first on the **Upload Dataset** page.")
    else:
        numeric_df = df.select_dtypes(include="number")
        categorical_df = df.select_dtypes(exclude="number")

        # -----------------------------------------------------------
        # SUMMARY STATISTICS
        # -----------------------------------------------------------
        st.subheader("📋 Summary Statistics")

        if numeric_df.empty:
            st.info("No numeric columns available for summary statistics.")
        else:
            # .describe() gives count, mean, std, min, 25/50/75%, max
            # .T transposes it so columns become rows — easier to read
            # when there are many numeric columns.
            st.dataframe(numeric_df.describe().T.round(2), use_container_width=True)

        st.markdown("---")

        # -----------------------------------------------------------
        # MISSING VALUE HEATMAP
        # -----------------------------------------------------------
        st.subheader("🕳️ Missing Value Heatmap")

        if df.isnull().sum().sum() == 0:
            st.success("No missing values in this dataset — nothing to visualize here.")
        else:
            # missingno.matrix draws a visual grid: white gaps = missing values,
            # colored bars = present values. Great for spotting patterns of
            # missingness across rows and columns at a glance.
            fig, ax = plt.subplots(figsize=(10, 4))
            msno.matrix(df, ax=ax, sparkline=False)
            st.pyplot(fig)
            plt.close(fig)  # free memory — important when generating many plots

        st.markdown("---")

        # -----------------------------------------------------------
        # CORRELATION MATRIX + HEATMAP
        # -----------------------------------------------------------
        st.subheader("🔗 Correlation Matrix")

        if numeric_df.shape[1] < 2:
            st.info("Need at least 2 numeric columns to compute correlations.")
        else:
            corr_matrix = numeric_df.corr()

            fig, ax = plt.subplots(figsize=(5, 3.5))
            # annot=True prints the actual correlation numbers inside each cell
            # cmap="coolwarm" makes negative correlations blue, positive red
            sns.heatmap(
                corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                ax=ax, annot_kws={"size": 7}, cbar_kws={"shrink": 0.8},
            )
            ax.tick_params(labelsize=7)

            # Wrapping in a narrower column forces Streamlit to actually
            # respect a smaller display width, instead of stretching the
            # image to fill the full page width.
            heatmap_col, _ = st.columns([1, 1])
            with heatmap_col:
                st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            # -------------------------------------------------------
            # PLAIN-ENGLISH CORRELATION INSIGHTS
            # Rule-based: scan the correlation matrix for pairs above
            # a threshold and turn them into readable sentences.
            # No LLM involved — purely programmatic logic.
            # -------------------------------------------------------
            st.markdown("##### 💬 Correlation Insights")

            insight_threshold = 0.5
            found_insight = False
            already_reported = set()  # avoids reporting A-B and B-A twice

            for col_a in corr_matrix.columns:
                for col_b in corr_matrix.columns:
                    if col_a == col_b:
                        continue
                    pair_key = frozenset([col_a, col_b])
                    if pair_key in already_reported:
                        continue

                    corr_value = corr_matrix.loc[col_a, col_b]

                    if abs(corr_value) >= insight_threshold:
                        already_reported.add(pair_key)
                        found_insight = True

                        if corr_value > 0:
                            direction = "increases"
                            strength = "strong" if corr_value >= 0.7 else "moderate"
                        else:
                            direction = "decreases"
                            strength = "strong" if corr_value <= -0.7 else "moderate"

                        # Escape "$" so Streamlit's markdown renderer doesn't
                        # interpret it as the start of LaTeX math notation
                        # (a common issue with column names like "Income ($)").
                        safe_col_a = col_a.replace("$", "\\$")
                        safe_col_b = col_b.replace("$", "\\$")

                        st.write(
                            f"- There is a **{strength} {'positive' if corr_value > 0 else 'negative'} "
                            f"correlation** ({corr_value:.2f}) between **{safe_col_a}** and **{safe_col_b}** — "
                            f"as {safe_col_a} increases, {safe_col_b} typically **{direction}**."
                        )

            if not found_insight:
                st.write("No strong correlations (|r| ≥ 0.5) were found between numeric columns.")

        st.markdown("---")

        # -----------------------------------------------------------
        # HISTOGRAMS — DISTRIBUTION ANALYSIS
        # -----------------------------------------------------------
        st.subheader("📊 Distribution Analysis (Histograms)")

        if numeric_df.empty:
            st.info("No numeric columns available for histograms.")
        else:
            selected_hist_col = st.selectbox(
                "Select a column to view its distribution:",
                options=numeric_df.columns.tolist(),
                key="hist_col_selector",
            )

            fig, ax = plt.subplots(figsize=(5, 3))
            sns.histplot(numeric_df[selected_hist_col].dropna(), kde=True, ax=ax, color="#4C72B0")
            ax.set_title(f"Distribution of {selected_hist_col}", fontsize=9)
            ax.tick_params(labelsize=7)

            hist_col, _ = st.columns([1, 1])
            with hist_col:
                st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.markdown("---")

        # -----------------------------------------------------------
        # BOXPLOTS — VISUAL OUTLIER CHECK
        # -----------------------------------------------------------
        st.subheader("📦 Boxplots (Outlier Visualization)")

        if numeric_df.empty:
            st.info("No numeric columns available for boxplots.")
        else:
            selected_box_col = st.selectbox(
                "Select a column to view its boxplot:",
                options=numeric_df.columns.tolist(),
                key="box_col_selector",
            )

            fig, ax = plt.subplots(figsize=(5, 2.5))
            sns.boxplot(x=numeric_df[selected_box_col].dropna(), ax=ax, color="#DD8452")
            ax.set_title(f"Boxplot of {selected_box_col}", fontsize=9)
            ax.tick_params(labelsize=7)

            box_col, _ = st.columns([1, 1])
            with box_col:
                st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.markdown("---")

        # -----------------------------------------------------------
        # CATEGORICAL ANALYSIS
        # -----------------------------------------------------------
        st.subheader("🗂️ Categorical Analysis")

        if categorical_df.empty:
            st.info("No categorical (text) columns available for analysis.")
        else:
            selected_cat_col = st.selectbox(
                "Select a categorical column to view its value counts:",
                options=categorical_df.columns.tolist(),
                key="cat_col_selector",
            )

            value_counts = df[selected_cat_col].value_counts().head(15)  # top 15 to avoid overcrowding

            fig, ax = plt.subplots(figsize=(5, 3))
            sns.barplot(x=value_counts.values, y=value_counts.index, ax=ax, color="#55A868")
            ax.set_title(f"Top values in {selected_cat_col}", fontsize=9)
            ax.tick_params(labelsize=7)

            cat_col, _ = st.columns([1, 1])
            with cat_col:
                st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.markdown("---")

        # -----------------------------------------------------------
        # SKEWNESS & KURTOSIS
        # -----------------------------------------------------------
        st.subheader("📐 Skewness & Kurtosis")

        if numeric_df.empty:
            st.info("No numeric columns available.")
        else:
            skew_kurt_df = pd.DataFrame({
                "Column": numeric_df.columns,
                "Skewness": numeric_df.skew().round(2).values,
                "Kurtosis": numeric_df.kurt().round(2).values,
            })
            st.dataframe(skew_kurt_df, use_container_width=True, hide_index=True)
            st.caption(
                "Skewness: ~0 = symmetric, >0.5 = right-skewed, <-0.5 = left-skewed. "
                "Kurtosis: ~0 = normal-like tails, >0 = heavier tails (more extreme outliers)."
            )

elif page == "📌 KPIs":
    st.title("📌 Automatic KPI Generator")

    if st.session_state.cleaned_df is not None:
        df = st.session_state.cleaned_df
    elif st.session_state.df is not None:
        df = st.session_state.df
    else:
        df = None

    if df is None:
        st.info("👆 Please upload a dataset first on the **Upload Dataset** page.")
    else:
        # -----------------------------------------------------------
        # DATASET TYPE DETECTION
        # Rule-based keyword scoring — no ML involved.
        # We check how many keywords for each dataset type appear
        # anywhere in the column names (case-insensitive substring match).
        # -----------------------------------------------------------
        columns_lower = " ".join(df.columns).lower()

        type_keywords = {
            "Retail": ["product", "price", "quantity", "sales", "revenue", "category", "order"],
            "HR": ["employee", "salary", "department", "hire", "attrition", "performance", "tenure"],
            "Finance": ["revenue", "expense", "profit", "budget", "cost", "transaction", "invoice"],
            "Customer": ["customer", "spending", "income", "age", "gender", "genre", "membership"],
        }

        scores = {}
        for dataset_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in columns_lower)
            scores[dataset_type] = score

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Require at least 2 keyword matches before trusting a specific type;
        # otherwise fall back to "Generic" rather than guessing wrong.
        detected_type = best_type if best_score >= 2 else "Generic"

        st.info(f"🔍 Detected dataset type: **{detected_type}** (keyword match score: {best_score})")

        with st.expander("How was this detected?"):
            score_df = pd.DataFrame({
                "Dataset Type": scores.keys(),
                "Keyword Matches": scores.values(),
            }).sort_values("Keyword Matches", ascending=False)
            st.dataframe(score_df, use_container_width=True, hide_index=True)
            st.caption(
                "Detection works by scanning column names for keywords typically "
                "associated with each dataset type. The type with the most matches "
                "wins, as long as it clears a minimum threshold of 2 matches."
            )

        st.markdown("---")
        st.subheader(f"📊 {detected_type} KPIs")

        # Helper: find the first column whose name contains any of the given
        # keywords. Returns None if nothing matches. Used throughout to
        # flexibly locate the "right" column regardless of exact naming.
        def find_column(dataframe, keywords):
            for col in dataframe.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in keywords):
                    return col
            return None

        if detected_type == "Customer":
            customer_col = find_column(df, ["customer", "id"])
            age_col = find_column(df, ["age"])
            income_col = find_column(df, ["income"])
            spending_col = find_column(df, ["spending"])
            gender_col = find_column(df, ["gender", "genre"])

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Customers", f"{df.shape[0]:,}")
            with col2:
                if age_col:
                    st.metric("Average Age", f"{df[age_col].mean():.1f} yrs")
                else:
                    st.metric("Average Age", "N/A")
            with col3:
                if income_col:
                    st.metric("Average Income", f"{df[income_col].mean():.1f}")
                else:
                    st.metric("Average Income", "N/A")
            with col4:
                if spending_col:
                    st.metric("Avg Spending Score", f"{df[spending_col].mean():.1f}")
                else:
                    st.metric("Avg Spending Score", "N/A")

            if gender_col:
                st.markdown("##### Gender Distribution")
                st.bar_chart(df[gender_col].value_counts())

        elif detected_type == "Retail":
            price_col = find_column(df, ["price"])
            quantity_col = find_column(df, ["quantity", "qty"])
            revenue_col = find_column(df, ["revenue", "sales"])
            category_col = find_column(df, ["category"]) or find_column(df, ["product"])

            # If there's no explicit revenue column but we DO have price and
            # quantity, we can calculate revenue ourselves.
            calculated_revenue = None
            if revenue_col:
                calculated_revenue = df[revenue_col].sum()
            elif price_col and quantity_col:
                calculated_revenue = (df[price_col] * df[quantity_col]).sum()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Orders", f"{df.shape[0]:,}")
            with col2:
                if calculated_revenue is not None:
                    st.metric("Total Revenue", f"{calculated_revenue:,.2f}")
                else:
                    st.metric("Total Revenue", "N/A")
            with col3:
                if quantity_col:
                    st.metric("Total Units Sold", f"{df[quantity_col].sum():,.0f}")
                else:
                    st.metric("Total Units Sold", "N/A")
            with col4:
                if calculated_revenue is not None and df.shape[0] > 0:
                    st.metric("Avg Order Value", f"{calculated_revenue / df.shape[0]:,.2f}")
                else:
                    st.metric("Avg Order Value", "N/A")

            if category_col:
                st.markdown(f"##### Top {category_col} by Count")
                st.bar_chart(df[category_col].value_counts().head(10))

        elif detected_type == "HR":
            salary_col = find_column(df, ["salary"])
            department_col = find_column(df, ["department"])
            attrition_col = find_column(df, ["attrition", "status"])
            tenure_col = find_column(df, ["tenure", "years"])

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Employees", f"{df.shape[0]:,}")
            with col2:
                if salary_col:
                    st.metric("Average Salary", f"{df[salary_col].mean():,.2f}")
                else:
                    st.metric("Average Salary", "N/A")
            with col3:
                if attrition_col:
                    # Look for common "left the company" indicators:
                    # Yes/No, True/False, or Terminated/Active style values.
                    left_values = ["yes", "true", "terminated", "resigned", "left"]
                    attrition_mask = df[attrition_col].astype(str).str.lower().isin(left_values)
                    attrition_rate = (attrition_mask.sum() / len(df)) * 100
                    st.metric("Attrition Rate", f"{attrition_rate:.1f}%")
                else:
                    st.metric("Attrition Rate", "N/A")
            with col4:
                if tenure_col:
                    st.metric("Average Tenure", f"{df[tenure_col].mean():.1f} yrs")
                else:
                    st.metric("Average Tenure", "N/A")

            if department_col:
                st.markdown(f"##### Employees by {department_col}")
                st.bar_chart(df[department_col].value_counts())

        elif detected_type == "Finance":
            revenue_col = find_column(df, ["revenue", "sales", "income"])
            expense_col = find_column(df, ["expense", "cost"])
            profit_col = find_column(df, ["profit"])

            total_revenue = df[revenue_col].sum() if revenue_col else None
            total_expense = df[expense_col].sum() if expense_col else None

            # Prefer an explicit profit column if it exists; otherwise
            # derive it as revenue minus expenses.
            if profit_col:
                total_profit = df[profit_col].sum()
            elif total_revenue is not None and total_expense is not None:
                total_profit = total_revenue - total_expense
            else:
                total_profit = None

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if total_revenue is not None:
                    st.metric("Total Revenue", f"{total_revenue:,.2f}")
                else:
                    st.metric("Total Revenue", "N/A")
            with col2:
                if total_expense is not None:
                    st.metric("Total Expenses", f"{total_expense:,.2f}")
                else:
                    st.metric("Total Expenses", "N/A")
            with col3:
                if total_profit is not None:
                    st.metric("Net Profit", f"{total_profit:,.2f}")
                else:
                    st.metric("Net Profit", "N/A")
            with col4:
                if total_profit is not None and total_revenue not in (None, 0):
                    profit_margin = (total_profit / total_revenue) * 100
                    st.metric("Profit Margin", f"{profit_margin:.1f}%")
                else:
                    st.metric("Profit Margin", "N/A")

        else:  # detected_type == "Generic"
            st.caption(
                "This dataset didn't clearly match a specific business category, "
                "so here are general-purpose statistics instead."
            )

            numeric_cols_kpi = df.select_dtypes(include="number").columns.tolist()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{df.shape[0]:,}")
            with col2:
                st.metric("Total Columns", f"{df.shape[1]:,}")
            with col3:
                st.metric("Numeric Columns", f"{len(numeric_cols_kpi):,}")
            with col4:
                total_nulls = int(df.isnull().sum().sum())
                st.metric("Total Missing Values", f"{total_nulls:,}")

            if numeric_cols_kpi:
                st.markdown("##### Average Values (Numeric Columns)")
                averages = df[numeric_cols_kpi].mean().round(2)
                st.bar_chart(averages)

elif page == "📊 Dashboard":
    st.title("📊 Interactive Dashboard")

    if st.session_state.cleaned_df is not None:
        base_df = st.session_state.cleaned_df
    elif st.session_state.df is not None:
        base_df = st.session_state.df
    else:
        base_df = None

    if base_df is None:
        st.info("👆 Please upload a dataset first on the **Upload Dataset** page.")
    else:
        numeric_cols = base_df.select_dtypes(include="number").columns.tolist()
        categorical_cols = base_df.select_dtypes(exclude="number").columns.tolist()

        # -----------------------------------------------------------
        # FILTERS
        # Applied once, at the top, then reused by every chart below —
        # this is what makes the whole dashboard feel "connected."
        # -----------------------------------------------------------
        st.subheader("🔍 Filters")

        filtered_df = base_df.copy()

        if categorical_cols:
            filter_col = st.selectbox(
                "Filter by column (optional):",
                options=["None"] + categorical_cols,
            )

            if filter_col != "None":
                unique_values = base_df[filter_col].dropna().unique().tolist()
                selected_values = st.multiselect(
                    f"Select {filter_col} value(s) to include:",
                    options=unique_values,
                    default=unique_values,  # start with everything selected
                )
                # Only rows whose value is in the selected list survive the filter
                filtered_df = filtered_df[filtered_df[filter_col].isin(selected_values)]

        st.caption(f"Showing {filtered_df.shape[0]:,} of {base_df.shape[0]:,} rows after filtering.")

        st.markdown("---")

        # -----------------------------------------------------------
        # BAR CHART
        # -----------------------------------------------------------
        st.subheader("📊 Bar Chart")

        if categorical_cols and numeric_cols:
            bar_col1, bar_col2 = st.columns(2)
            with bar_col1:
                bar_x = st.selectbox("X-axis (category):", options=categorical_cols, key="bar_x")
            with bar_col2:
                bar_y = st.selectbox("Y-axis (numeric):", options=numeric_cols, key="bar_y")

            # Aggregate: sum of the numeric column, grouped by the category
            bar_data = filtered_df.groupby(bar_x, as_index=False)[bar_y].sum()

            fig_bar = px.bar(
                bar_data, x=bar_x, y=bar_y,
                title=f"Total {bar_y} by {bar_x}",
                color=bar_x,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Need at least one categorical and one numeric column for a bar chart.")

        st.markdown("---")

        # -----------------------------------------------------------
        # LINE CHART
        # -----------------------------------------------------------
        st.subheader("📈 Line Chart")

        if numeric_cols:
            line_col1, line_col2 = st.columns(2)
            with line_col1:
                # Allow using either a numeric or datetime column as the x-axis
                line_x_options = filtered_df.columns.tolist()
                line_x = st.selectbox("X-axis:", options=line_x_options, key="line_x")
            with line_col2:
                line_y = st.selectbox("Y-axis (numeric):", options=numeric_cols, key="line_y")

            # Sort by the x-axis so the line draws in a sensible order
            # (important if x is a date or sequential ID column)
            line_data = filtered_df.sort_values(by=line_x)

            fig_line = px.line(
                line_data, x=line_x, y=line_y,
                title=f"{line_y} over {line_x}",
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Need at least one numeric column for a line chart.")

        st.markdown("---")

        # -----------------------------------------------------------
        # PIE CHART
        # -----------------------------------------------------------
        st.subheader("🥧 Pie Chart")

        if categorical_cols:
            pie_col = st.selectbox("Column to break down:", options=categorical_cols, key="pie_col")

            pie_data = filtered_df[pie_col].value_counts().reset_index()
            pie_data.columns = [pie_col, "count"]

            fig_pie = px.pie(
                pie_data, names=pie_col, values="count",
                title=f"Distribution of {pie_col}",
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Need at least one categorical column for a pie chart.")

        st.markdown("---")

        # -----------------------------------------------------------
        # SCATTER CHART
        # -----------------------------------------------------------
        st.subheader("🔵 Scatter Chart")

        if len(numeric_cols) >= 2:
            scatter_col1, scatter_col2, scatter_col3 = st.columns(3)
            with scatter_col1:
                scatter_x = st.selectbox("X-axis:", options=numeric_cols, key="scatter_x")
            with scatter_col2:
                scatter_y = st.selectbox(
                    "Y-axis:", options=numeric_cols,
                    index=min(1, len(numeric_cols) - 1),  # default to 2nd numeric col if available
                    key="scatter_y",
                )
            with scatter_col3:
                color_options = ["None"] + categorical_cols
                scatter_color = st.selectbox("Color by (optional):", options=color_options, key="scatter_color")

            fig_scatter = px.scatter(
                filtered_df, x=scatter_x, y=scatter_y,
                color=None if scatter_color == "None" else scatter_color,
                title=f"{scatter_y} vs {scatter_x}",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Need at least two numeric columns for a scatter chart.")

        st.markdown("---")

        # -----------------------------------------------------------
        # INTERACTIVE HEATMAP
        # -----------------------------------------------------------
        st.subheader("🌡️ Correlation Heatmap")

        if len(numeric_cols) >= 2:
            corr_data = filtered_df[numeric_cols].corr()

            fig_heatmap = px.imshow(
                corr_data,
                text_auto=".2f",  # show correlation values inside each cell
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,  # fix the color scale to the full correlation range
                title="Correlation Heatmap",
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Need at least two numeric columns for a heatmap.")

        st.markdown("---")

        # -----------------------------------------------------------
        # BOXPLOT (OPTIONALLY GROUPED)
        # -----------------------------------------------------------
        st.subheader("📦 Boxplot")

        if numeric_cols:
            box_col1, box_col2 = st.columns(2)
            with box_col1:
                box_y = st.selectbox("Numeric column:", options=numeric_cols, key="dash_box_y")
            with box_col2:
                box_group_options = ["None"] + categorical_cols
                box_group = st.selectbox("Group by (optional):", options=box_group_options, key="dash_box_group")

            fig_box = px.box(
                filtered_df, y=box_y,
                x=None if box_group == "None" else box_group,
                title=f"Boxplot of {box_y}" + (f" by {box_group}" if box_group != "None" else ""),
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("Need at least one numeric column for a boxplot.")

        st.markdown("---")

        # -----------------------------------------------------------
        # HISTOGRAM (WITH ADJUSTABLE BINS)
        # -----------------------------------------------------------
        st.subheader("📊 Histogram")

        if numeric_cols:
            hist_col1, hist_col2 = st.columns(2)
            with hist_col1:
                dash_hist_col = st.selectbox("Column:", options=numeric_cols, key="dash_hist_col")
            with hist_col2:
                bin_count = st.slider("Number of bins:", min_value=5, max_value=100, value=30)

            fig_hist = px.histogram(
                filtered_df, x=dash_hist_col, nbins=bin_count,
                title=f"Histogram of {dash_hist_col}",
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Need at least one numeric column for a histogram.")

elif page == "💡 Insights":
    st.title("💡 Business Insight Generator")
    st.caption("All insights below are generated using rule-based statistical logic — no AI/LLM involved.")

    if st.session_state.cleaned_df is not None:
        df = st.session_state.cleaned_df
    elif st.session_state.df is not None:
        df = st.session_state.df
    else:
        df = None

    if df is None:
        st.info("👆 Please upload a dataset first on the **Upload Dataset** page.")
    else:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

        # -----------------------------------------------------------
        # EXCLUDE ID-LIKE COLUMNS
        # A column where nearly every value is unique (e.g., CustomerID)
        # is almost certainly an identifier, not a meaningful measure —
        # including it in insights produces statistically "true" but
        # business-meaningless statements (e.g., "highest CustomerID").
        # We exclude any numeric column where >95% of values are unique,
        # and also any column whose name literally contains "id".
        # -----------------------------------------------------------
        def is_id_like(col):
            if "id" in col.lower():
                return True
            uniqueness_ratio = df[col].nunique() / len(df)
            return uniqueness_ratio > 0.95

        numeric_cols = [col for col in numeric_cols if not is_id_like(col)]

        def esc(text):
            """Escape '$' so Streamlit markdown doesn't treat it as LaTeX math."""
            return str(text).replace("$", "\\$")

        insights = []  # collects (insight_text) strings to display at the end

        # -----------------------------------------------------------
        # RULE 1: TOP / BOTTOM PERFORMER BY CATEGORY
        # For each numeric column, grouped by each categorical column,
        # find which category has the highest and lowest average.
        # -----------------------------------------------------------
        for num_col in numeric_cols[:3]:      # limit to first 3 numeric cols to avoid an overwhelming report
            for cat_col in categorical_cols[:2]:  # limit to first 2 categorical cols
                grouped = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
                if len(grouped) < 2:
                    continue  # need at least 2 groups to compare

                top_group, top_value = grouped.index[0], grouped.iloc[0]
                bottom_group, bottom_value = grouped.index[-1], grouped.iloc[-1]

                insights.append(
                    f"📌 **{esc(top_group)}** has the highest average **{esc(num_col)}** "
                    f"({top_value:,.2f}) when grouped by **{esc(cat_col)}**, while "
                    f"**{esc(bottom_group)}** has the lowest ({bottom_value:,.2f})."
                )

        # -----------------------------------------------------------
        # RULE 2: EXTREME INDIVIDUAL VALUES
        # Finds the single row with the highest/lowest value in a
        # numeric column — useful for flagging standout records.
        # -----------------------------------------------------------
        for num_col in numeric_cols[:3]:
            max_idx = df[num_col].idxmax()
            min_idx = df[num_col].idxmin()

            max_val = df.loc[max_idx, num_col]
            min_val = df.loc[min_idx, num_col]

            insights.append(
                f"📈 The highest recorded **{esc(num_col)}** is **{max_val:,.2f}** "
                f"(row {max_idx}), and the lowest is **{min_val:,.2f}** (row {min_idx})."
            )

        # -----------------------------------------------------------
        # RULE 3: CATEGORICAL DOMINANCE
        # Finds which category makes up the largest share of the
        # dataset for each categorical column.
        # -----------------------------------------------------------
        for cat_col in categorical_cols[:3]:
            value_counts = df[cat_col].value_counts(normalize=True)
            if value_counts.empty:
                continue

            top_category = value_counts.index[0]
            top_share = value_counts.iloc[0] * 100

            insights.append(
                f"🗂️ **{esc(top_category)}** is the most common value in **{esc(cat_col)}**, "
                f"making up **{top_share:.1f}%** of all records."
            )

        # -----------------------------------------------------------
        # RULE 4: CORRELATION-BASED INSIGHTS
        # Reuses the same |r| >= 0.5 threshold logic from Module 4,
        # phrased as a business-relevant relationship.
        # -----------------------------------------------------------
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            reported_pairs = set()

            for col_a in corr_matrix.columns:
                for col_b in corr_matrix.columns:
                    if col_a == col_b:
                        continue
                    pair_key = frozenset([col_a, col_b])
                    if pair_key in reported_pairs:
                        continue

                    corr_value = corr_matrix.loc[col_a, col_b]
                    if abs(corr_value) >= 0.5:
                        reported_pairs.add(pair_key)
                        relation = "rises" if corr_value > 0 else "falls"
                        insights.append(
                            f"🔗 When **{esc(col_a)}** increases, **{esc(col_b)}** typically "
                            f"**{relation}** (correlation: {corr_value:.2f})."
                        )

        # -----------------------------------------------------------
        # RULE 5: GROUP COMPARISON (ABOVE/BELOW MEDIAN)
        # Splits one numeric column into "above" and "below" median
        # groups, then compares the average of another numeric column
        # between the two groups.
        # -----------------------------------------------------------
        if len(numeric_cols) >= 2:
            split_col = numeric_cols[0]
            compare_col = numeric_cols[1]

            median_val = df[split_col].median()
            above_group = df[df[split_col] > median_val][compare_col].mean()
            below_group = df[df[split_col] <= median_val][compare_col].mean()

            if pd.notna(above_group) and pd.notna(below_group) and below_group != 0:
                pct_diff = ((above_group - below_group) / abs(below_group)) * 100
                direction = "higher" if pct_diff > 0 else "lower"

                insights.append(
                    f"⚖️ Records with **{esc(split_col)}** above the median tend to have "
                    f"**{abs(pct_diff):.1f}% {direction}** average **{esc(compare_col)}** "
                    f"compared to those below the median."
                )

        # -----------------------------------------------------------
        # DISPLAY ALL INSIGHTS
        # -----------------------------------------------------------
        st.markdown("---")
        st.subheader(f"📋 Generated Insights ({len(insights)} found)")

        if not insights:
            st.info("Not enough data variety to generate insights for this dataset.")
        else:
            for insight in insights:
                st.markdown(f"- {insight}")

else:
    # Placeholder for all remaining not-yet-built pages
    st.title(page)
    st.warning(f"🚧 The **{page}** module hasn't been built yet. Coming in a future step!")