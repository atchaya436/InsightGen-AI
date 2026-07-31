"""
InsightGen AI: Automated Business Intelligence & Decision Support Platform
Module 1: Base application shell (title, description, sidebar, navigation)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

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

else:
    # Placeholder for all remaining not-yet-built pages
    st.title(page)
    st.warning(f"🚧 The **{page}** module hasn't been built yet. Coming in a future step!")