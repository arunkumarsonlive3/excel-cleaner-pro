import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import re

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="Excel Data Cleaner Pro",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp { background: #0a0f1e; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Main container */
.block-container { padding: 2rem 3rem; max-width: 1200px; }

/* Hero section */
.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffd700, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-sub {
    color: #8899bb;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Cards */
.stat-card {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.stat-num { font-size: 2rem; font-weight: 700; color: #ffd700; }
.stat-label { color: #8899bb; font-size: 0.85rem; }

/* Issue cards */
.issue-card {
    background: #111827;
    border-left: 4px solid #e63946;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    color: #fff;
}
.fix-card {
    background: #0d1f0d;
    border-left: 4px solid #2dc653;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    color: #fff;
}

/* Password gate */
.lock-box {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    max-width: 480px;
    margin: 6rem auto;
}
.lock-icon { font-size: 4rem; margin-bottom: 1rem; }
.lock-title { color: #fff; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; }
.lock-sub { color: #8899bb; margin-bottom: 2rem; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ffd700, #ff9500) !important;
    color: #0a0f1e !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-size: 1rem !important;
    transition: transform 0.2s !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; }

/* Upload box */
.uploadedFile { background: #111827 !important; border-radius: 8px !important; }
[data-testid="stFileUploader"] {
    background: #111827;
    border: 2px dashed #1e3a5f;
    border-radius: 12px;
    padding: 1rem;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: #111827 !important;
    color: #8899bb !important;
    border-radius: 8px 8px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #ffd700 !important;
}

/* Dataframe */
.stDataFrame { background: #111827 !important; }

/* Input */
.stTextInput input {
    background: #1a2340 !important;
    color: #fff !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
}

/* Selectbox */
.stSelectbox select, [data-baseweb="select"] {
    background: #1a2340 !important;
    color: #fff !important;
}

/* Progress */
.stProgress > div > div { background: #ffd700 !important; }

/* Section headers */
.section-header {
    color: #ffd700;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e3a5f;
}

/* Badge */
.badge {
    display: inline-block;
    background: #1e3a5f;
    color: #7eb8f7;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    margin: 0.2rem;
}

/* Success/Error messages */
.stSuccess { background: #0d1f0d !important; border-left-color: #2dc653 !important; }
.stError { background: #1f0d0d !important; }
.stWarning { background: #1f1a0d !important; }
.stInfo { background: #0d1527 !important; }
</style>
""", unsafe_allow_html=True)

# ─── PASSWORD GATE ───
ACCESS_CODE = "DACLEAN2024"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="lock-box">
        <div class="lock-icon">🔐</div>
        <div class="lock-title">Excel Data Cleaner Pro</div>
        <div class="lock-sub">Enter your access code to continue</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        code = st.text_input("Access Code", type="password", placeholder="Enter code here...")
        if st.button("🚀 Unlock Tool", use_container_width=True):
            if code == ACCESS_CODE:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid access code. Purchase at gumroad.com/l/daclean")
    st.stop()

# ─── MAIN APP ───

# Header
st.markdown("""
<div class="hero-title">🧹 Excel Data Cleaner Pro</div>
<div class="hero-sub">Upload messy data → Get clean data in seconds. No Python needed.</div>
""", unsafe_allow_html=True)

# Upload section
st.markdown('<div class="section-header">📁 Upload Your File</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop your Excel or CSV file here",
    type=['csv', 'xlsx', 'xls'],
    help="Supports .csv, .xlsx, .xls files up to 200MB"
)

if uploaded:
    # Load data
    try:
        if uploaded.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded)
        else:
            df_raw = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    df = df_raw.copy()

    # ─── STATS ROW ───
    total_cells = df.shape[0] * df.shape[1]
    null_count = df.isnull().sum().sum()
    dup_count = df.duplicated().sum()
    col_count = df.shape[1]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{df.shape[0]:,}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{col_count}</div><div class="stat-label">Columns</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#e63946">{null_count:,}</div><div class="stat-label">Missing Values</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#e63946">{dup_count:,}</div><div class="stat-label">Duplicates</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── TABS ───
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Issues Found", "🛠️ Clean Settings", "✅ Cleaned Data", "📊 Summary Report"])

    with tab1:
        st.markdown('<div class="section-header">Issues Detected in Your Data</div>', unsafe_allow_html=True)

        issues = []

        # Missing values
        null_cols = df.isnull().sum()
        null_cols = null_cols[null_cols > 0]
        if not null_cols.empty:
            for col, count in null_cols.items():
                pct = round(count / len(df) * 100, 1)
                issues.append(('missing', col, count, pct))
                st.markdown(f'<div class="issue-card">⚠️ <b>{col}</b> — {count} missing values ({pct}%)</div>', unsafe_allow_html=True)

        # Duplicates
        if dup_count > 0:
            st.markdown(f'<div class="issue-card">🔁 <b>{dup_count} duplicate rows</b> found</div>', unsafe_allow_html=True)

        # Whitespace
        str_cols = df.select_dtypes(include='object').columns
        ws_cols = []
        for col in str_cols:
            has_ws = df[col].dropna().apply(lambda x: str(x) != str(x).strip()).any()
            if has_ws:
                ws_cols.append(col)
                st.markdown(f'<div class="issue-card">〰️ <b>{col}</b> — has leading/trailing whitespace</div>', unsafe_allow_html=True)

        # Mixed types
        for col in str_cols:
            sample = df[col].dropna().head(100)
            num_like = sample.apply(lambda x: str(x).replace('.','',1).replace('-','',1).isdigit()).sum()
            if 0 < num_like < len(sample) * 0.8 and num_like > len(sample) * 0.2:
                st.markdown(f'<div class="issue-card">🔀 <b>{col}</b> — mixed text and numbers detected</div>', unsafe_allow_html=True)

        if not issues and dup_count == 0 and not ws_cols:
            st.success("✅ Your data looks clean! No major issues found.")

    with tab2:
        st.markdown('<div class="section-header">Choose Cleaning Options</div>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("**Missing Values**")
            missing_strategy = st.selectbox(
                "How to handle missing values?",
                ["Drop rows with missing values", "Fill numbers with Mean", "Fill numbers with Median", "Fill numbers with 0", "Fill text with 'Unknown'", "Keep as is"]
            )

            st.markdown("**Duplicates**")
            remove_dups = st.checkbox("Remove duplicate rows", value=True)

            st.markdown("**Text Cleaning**")
            trim_ws = st.checkbox("Trim whitespace from text columns", value=True)
            to_lower = st.checkbox("Convert text to lowercase", value=False)
            to_upper = st.checkbox("Convert text to UPPERCASE", value=False)

        with col_r:
            st.markdown("**Column Names**")
            clean_colnames = st.checkbox("Clean column names (remove spaces, special chars)", value=True)
            strip_colnames = st.checkbox("Strip whitespace from column names", value=True)

            st.markdown("**Data Types**")
            fix_dates = st.checkbox("Auto-detect and fix date columns", value=True)
            fix_nums = st.checkbox("Convert numeric-looking text to numbers", value=True)

            st.markdown("**Filters**")
            drop_empty_cols = st.checkbox("Drop columns that are 100% empty", value=True)
            drop_empty_rows = st.checkbox("Drop rows that are 100% empty", value=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Clean My Data Now!", use_container_width=True):
            with st.spinner("Cleaning your data..."):
                cleaned = df.copy()
                changes = []

                # Column names
                if strip_colnames:
                    cleaned.columns = [str(c).strip() for c in cleaned.columns]
                if clean_colnames:
                    cleaned.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', str(c)).strip('_') for c in cleaned.columns]
                    changes.append("✅ Column names cleaned")

                # Drop empty cols/rows
                if drop_empty_cols:
                    before = cleaned.shape[1]
                    cleaned.dropna(axis=1, how='all', inplace=True)
                    dropped = before - cleaned.shape[1]
                    if dropped > 0:
                        changes.append(f"✅ Dropped {dropped} completely empty column(s)")

                if drop_empty_rows:
                    before = len(cleaned)
                    cleaned.dropna(axis=0, how='all', inplace=True)
                    dropped = before - len(cleaned)
                    if dropped > 0:
                        changes.append(f"✅ Dropped {dropped} completely empty row(s)")

                # Duplicates
                if remove_dups:
                    before = len(cleaned)
                    cleaned.drop_duplicates(inplace=True)
                    removed = before - len(cleaned)
                    if removed > 0:
                        changes.append(f"✅ Removed {removed} duplicate row(s)")

                # Whitespace
                if trim_ws:
                    str_cols = cleaned.select_dtypes(include='object').columns
                    for col in str_cols:
                        cleaned[col] = cleaned[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
                    changes.append("✅ Trimmed whitespace from all text columns")

                # Case
                if to_lower:
                    str_cols = cleaned.select_dtypes(include='object').columns
                    for col in str_cols:
                        cleaned[col] = cleaned[col].str.lower()
                    changes.append("✅ Converted text to lowercase")
                elif to_upper:
                    str_cols = cleaned.select_dtypes(include='object').columns
                    for col in str_cols:
                        cleaned[col] = cleaned[col].str.upper()
                    changes.append("✅ Converted text to UPPERCASE")

                # Fix numeric columns
                if fix_nums:
                    str_cols = cleaned.select_dtypes(include='object').columns
                    for col in str_cols:
                        try:
                            converted = pd.to_numeric(cleaned[col], errors='coerce')
                            if converted.notna().sum() > len(cleaned) * 0.7:
                                cleaned[col] = converted
                        except:
                            pass
                    changes.append("✅ Converted numeric-looking columns to numbers")

                # Fix dates
                if fix_dates:
                    str_cols = cleaned.select_dtypes(include='object').columns
                    for col in str_cols:
                        try:
                            converted = pd.to_datetime(cleaned[col], errors='coerce', dayfirst=True)
                            if converted.notna().sum() > len(cleaned) * 0.7:
                                cleaned[col] = converted.dt.strftime('%Y-%m-%d')
                        except:
                            pass

                # Missing values
                num_cols = cleaned.select_dtypes(include=np.number).columns
                str_cols = cleaned.select_dtypes(include='object').columns

                if missing_strategy == "Drop rows with missing values":
                    before = len(cleaned)
                    cleaned.dropna(inplace=True)
                    changes.append(f"✅ Dropped {before - len(cleaned)} rows with missing values")
                elif missing_strategy == "Fill numbers with Mean":
                    for col in num_cols:
                        cleaned[col].fillna(cleaned[col].mean(), inplace=True)
                    changes.append("✅ Filled missing numbers with column mean")
                elif missing_strategy == "Fill numbers with Median":
                    for col in num_cols:
                        cleaned[col].fillna(cleaned[col].median(), inplace=True)
                    changes.append("✅ Filled missing numbers with column median")
                elif missing_strategy == "Fill numbers with 0":
                    for col in num_cols:
                        cleaned[col].fillna(0, inplace=True)
                    changes.append("✅ Filled missing numbers with 0")
                elif missing_strategy == "Fill text with 'Unknown'":
                    for col in str_cols:
                        cleaned[col].fillna('Unknown', inplace=True)
                    changes.append("✅ Filled missing text with 'Unknown'")

                st.session_state['cleaned_df'] = cleaned
                st.session_state['changes'] = changes
                st.session_state['original_df'] = df

            st.success("🎉 Data cleaned successfully! Go to 'Cleaned Data' tab to download.")

    with tab3:
        if 'cleaned_df' in st.session_state:
            cleaned = st.session_state['cleaned_df']
            changes = st.session_state['changes']

            # Changes made
            st.markdown('<div class="section-header">Changes Made</div>', unsafe_allow_html=True)
            for change in changes:
                st.markdown(f'<div class="fix-card">{change}</div>', unsafe_allow_html=True)

            # Before vs After stats
            st.markdown('<div class="section-header">Before vs After</div>', unsafe_allow_html=True)
            orig = st.session_state['original_df']

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Rows", cleaned.shape[0], delta=cleaned.shape[0] - orig.shape[0])
            with c2:
                st.metric("Columns", cleaned.shape[1], delta=cleaned.shape[1] - orig.shape[1])
            with c3:
                st.metric("Missing Values", cleaned.isnull().sum().sum(),
                    delta=cleaned.isnull().sum().sum() - orig.isnull().sum().sum())
            with c4:
                st.metric("Duplicates", cleaned.duplicated().sum(),
                    delta=cleaned.duplicated().sum() - orig.duplicated().sum())

            st.markdown('<div class="section-header">Cleaned Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(cleaned.head(50), use_container_width=True)

            # Download
            st.markdown('<div class="section-header">Download Cleaned File</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            with col1:
                # Excel download
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    cleaned.to_excel(writer, index=False, sheet_name='Cleaned Data')
                buffer.seek(0)
                st.download_button(
                    "⬇️ Download as Excel",
                    data=buffer,
                    file_name=f"cleaned_{uploaded.name.rsplit('.', 1)[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col2:
                # CSV download
                csv = cleaned.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Download as CSV",
                    data=csv,
                    file_name=f"cleaned_{uploaded.name.rsplit('.', 1)[0]}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("👆 Go to 'Clean Settings' tab and click 'Clean My Data Now!' first.")

    with tab4:
        st.markdown('<div class="section-header">📊 Data Summary Report</div>', unsafe_allow_html=True)

        # Column by column summary
        summary_data = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            nulls = df[col].isnull().sum()
            null_pct = round(nulls / len(df) * 100, 1)
            unique = df[col].nunique()
            sample = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A'

            summary_data.append({
                'Column': col,
                'Data Type': dtype,
                'Missing': nulls,
                'Missing %': f"{null_pct}%",
                'Unique Values': unique,
                'Sample Value': sample[:30]
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        # Download summary
        csv_summary = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download Summary Report",
            data=csv_summary,
            file_name="data_summary_report.csv",
            mime="text/csv"
        )

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0; color: #8899bb;">
        <div style="font-size: 5rem; margin-bottom: 1rem;">📂</div>
        <div style="font-size: 1.3rem; color: #fff; margin-bottom: 0.5rem;">Upload a file to get started</div>
        <div>Supports Excel (.xlsx, .xls) and CSV files</div>
        <br>
        <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap; margin-top:1rem;">
            <span class="badge">✅ Remove Duplicates</span>
            <span class="badge">✅ Fix Missing Values</span>
            <span class="badge">✅ Clean Column Names</span>
            <span class="badge">✅ Trim Whitespace</span>
            <span class="badge">✅ Fix Data Types</span>
            <span class="badge">✅ Download Clean File</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr style="border-color: #1e3a5f; margin-top: 3rem;">
<div style="text-align:center; color: #445566; font-size: 0.85rem; padding: 1rem 0;">
    Excel Data Cleaner Pro | Built for Data Analysts | 
    <a href="https://arunkumarsonlive.gumroad.com" style="color: #ffd700; text-decoration:none;">Get More DA Tools</a>
</div>
""", unsafe_allow_html=True)
