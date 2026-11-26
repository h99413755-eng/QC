import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# SAMPLE & LOCATION TRACKING SYSTEM
# Responsive UI | SQLite backend | Desktop / Tablet / Mobile
# ============================================================

st.set_page_config(
    page_title="SampleTrack | Quality Management",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(__file__).with_name("samples_database.db")

SAMPLE_TYPES = [
    "Underpad Sample",
    "Retention Sample",
    "Evaluation Sample",
    "Competitive Sample",
]

LOCATIONS = [
    "QC LAB A - Rack A", "QC LAB A - Rack B", "QC LAB A - Rack C",
    "QC LAB A -Rack D", "QC LAB - Rack E",
    "QC LAB B ", "QC LAB C","QC LAB D","QC LAB E","RETENTION ROOM -RACK A","RETENTION ROOM -RACK B","RETENTION ROOM -RACK C","RETENTION ROOM -RACK D",
"OTHERS",]

# --------------------------- STYLING -------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --navy: #14243A;
        --blue: #2563EB;
        --cyan: #06B6D4;
        --teal: #0F9D8A;
        --purple: #7657E8;
        --ink: #172B4D;
        --muted: #718096;
        --line: #E7EDF5;
        --surface: #FFFFFF;
        --canvas: #F4F7FC;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 90% 0%, rgba(37,99,235,.055), transparent 25%),
            var(--canvas);
        color: var(--ink);
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #14243A 0%, #1B3555 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }
    [data-testid="stSidebar"] * {
        color: #EAF1FC;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 10px;
        padding: 5px 8px;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,.14);
    }

    .brand {
        padding: 12px 8px 20px 8px;
    }
    .brand-icon {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        background: linear-gradient(135deg, #3B82F6, #06B6D4);
        box-shadow: 0 8px 22px rgba(6,182,212,.22);
        font-size: 25px;
        margin-bottom: 13px;
    }
    .brand-name {
        font-family: 'Manrope', sans-serif;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -.5px;
        color: white;
    }
    .brand-sub {
        font-size: 10px;
        letter-spacing: 1.5px;
        color: #AFC3DD;
        margin-top: 4px;
        font-weight: 700;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 22px;
        padding: 29px 32px;
        margin-bottom: 24px;
        color: white;
        background: linear-gradient(112deg, #172E4D 0%, #245AA1 58%, #168FA7 100%);
        box-shadow: 0 12px 32px rgba(23,61,105,.15);
    }
    .hero:after {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        right: -55px;
        top: -115px;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(255,255,255,.035),
                    0 0 0 58px rgba(255,255,255,.025);
    }
    .hero-eyebrow {
        color: #BFE7F6;
        font-size: 10px;
        letter-spacing: 2px;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .hero h1 {
        color: white !important;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(23px, 3vw, 32px);
        font-weight: 800;
        line-height: 1.2;
        margin: 0;
        letter-spacing: -.8px;
    }
    .hero p {
        color: #D9E9F8;
        font-size: 13px;
        margin: 9px 0 0 0;
        max-width: 650px;
    }

    .page-heading {
        font-family: 'Manrope', sans-serif;
        font-size: 21px;
        font-weight: 800;
        color: #172B4D;
        letter-spacing: -.4px;
        margin: 8px 0 3px 0;
    }
    .page-subtitle {
        font-size: 12px;
        color: #8290A5;
        margin-bottom: 18px;
    }
    .eyebrow {
        color: #8290A5;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 20px 0 10px;
    }

    .kpi-card {
        background: white;
        border: 1px solid #E8EEF6;
        border-radius: 17px;
        padding: 17px 18px;
        min-height: 125px;
        box-shadow: 0 5px 18px rgba(31,55,90,.045);
        transition: transform .18s ease, box-shadow .18s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(31,55,90,.09);
    }
    .kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 13px;
    }
    .kpi-label {
        color: #78879C;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .65px;
    }
    .kpi-icon {
        width: 36px;
        height: 36px;
        border-radius: 11px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 17px;
    }
    .kpi-value {
        color: #172B4D;
        font-family: 'Manrope', sans-serif;
        font-size: 29px;
        font-weight: 800;
        line-height: 1;
    }
    .kpi-foot {
        color: #94A0B1;
        font-size: 10px;
        margin-top: 9px;
    }

    .sample-card {
        background: white;
        border: 1px solid #E6ECF4;
        border-radius: 16px;
        padding: 18px;
        margin: 10px 0 13px 0;
        box-shadow: 0 4px 16px rgba(31,55,90,.04);
    }
    .sample-id {
        color: #2563EB;
        font-family: 'Manrope', sans-serif;
        font-size: 16px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }
    .sample-date {
        color: #95A1B2;
        font-size: 11px;
        margin-top: 3px;
    }
    .sample-meta {
        color: #4D5F78;
        font-size: 12px;
        margin-top: 12px;
        line-height: 1.9;
    }
    .tag {
        display: inline-block;
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 10px;
        font-weight: 800;
        margin: 7px 5px 0 0;
    }
    .tag-location { background: #EAF2FF; color: #2861B8; }
    .tag-status { background: #E6F7F0; color: #13845B; }

    div.stButton > button,
    div.stFormSubmitButton > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid #DCE6F2;
        transition: all .18s ease;
    }
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(100deg, #2563EB, #168FA7);
        border: 0;
        color: white;
    }
    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        border-color: #2563EB;
        color: #2563EB;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stTextArea"] textarea {
        border-radius: 10px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #E6ECF4;
        border-radius: 13px;
        overflow: hidden;
    }
    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #E6ECF4;
        border-radius: 17px;
        padding: 20px;
        box-shadow: 0 5px 18px rgba(31,55,90,.04);
    }
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem .85rem 2rem .85rem;
        }
        .hero {
            padding: 23px 20px;
            border-radius: 17px;
            margin-bottom: 17px;
        }
        .hero:after { right: -130px; }
        .kpi-card {
            padding: 14px;
            min-height: 112px;
            border-radius: 14px;
        }
        .kpi-value { font-size: 24px; }
        .kpi-label { font-size: 9px; }
        .sample-card { padding: 14px; }
        .page-heading { font-size: 19px; }
        div[data-testid="stForm"] { padding: 13px; }
        [data-testid="stSidebar"] { min-width: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- DATABASE ------------------------

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=20)

def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
                sample_id TEXT PRIMARY KEY,
                lot_number TEXT,
                sample_type TEXT,
                product_name TEXT,
                location TEXT,
                image_path TEXT,
                date TEXT
            )
            """
        )
        conn.commit()

def load_data():
    init_db()
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT sample_id, lot_number, sample_type, product_name,
                   location, image_path, date
            FROM samples
            ORDER BY date DESC
            """,
            conn,
        )
    return df.rename(
        columns={
            "sample_id": "Sample ID",
            "lot_number": "Lot Number",
            "sample_type": "Sample Type",
            "product_name": "Product Name",
            "location": "Location",
            "image_path": "Image Path",
            "date": "Date",
        }
    )

def save_record(record):
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO samples
                (sample_id, lot_number, sample_type, product_name,
                 location, image_path, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["Sample ID"],
                    record["Lot Number"],
                    record["Sample Type"],
                    record["Product Name"],
                    record["Location"],
                    record["Image Path"],
                    record["Date"],
                ),
            )
            conn.commit()
        return True, ""
    except sqlite3.IntegrityError:
        return False, "This Sample ID already exists. Please use a unique Sample ID."
    except Exception as exc:
        return False, f"Database error: {exc}"

# --------------------------- HELPERS -------------------------

def page_title(title, subtitle):
    st.markdown(
        f'<div class="page-heading">{title}</div>'
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )

def kpi_card(label, value, icon, color, note):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <div class="kpi-label">{label}</div>
                <div class="kpi-icon" style="background:{color}18;color:{color};">{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def display_sample(row, show_image=True):
    st.markdown('<div class="sample-card">', unsafe_allow_html=True)
    left, right = st.columns([2.3, 1], gap="medium")
    with left:
        st.markdown(
            f'<div class="sample-id">{row["Sample ID"]}</div>'
            f'<div class="sample-date">Registered: {row["Date"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="sample-meta">
                <b>Lot Number:</b> {row["Lot Number"]}<br>
                <b>Sample Type:</b> {row["Sample Type"]}<br>
                <b>Product:</b> {row["Product Name"] or "—"}
            </div>
            <span class="tag tag-location">📍 {row["Location"]}</span>
            <span class="tag tag-status">● REGISTERED</span>
            """,
            unsafe_allow_html=True,
        )
    with right:
        image_path = str(row.get("Image Path", "") or "").strip()
        if show_image and image_path:
            try:
                st.image(image_path, use_container_width=True)
            except Exception:
                st.caption("Image preview unavailable")
        elif show_image:
            st.caption("No sample image provided")
    st.markdown("</div>", unsafe_allow_html=True)

def refresh_data():
    st.session_state.samples_db = load_data()

# --------------------------- SESSION -------------------------

if "samples_db" not in st.session_state:
    st.session_state.samples_db = load_data()

df = st.session_state.samples_db.copy()

# --------------------------- SIDEBAR -------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">📦</div>
            <div class="brand-name">SampleTrack</div>
            <div class="brand-sub">QUALITY MANAGEMENT SYSTEM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("WORKSPACE")
    page = st.radio(
        "Main navigation",
        ["Dashboard", "Search Samples", "Register Sample", "Sample Database"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("SYSTEM INFORMATION")
    st.markdown("**Database**")
    st.caption("SQLite · Local storage")
    st.markdown("**Records**")
    st.caption(f"{len(df):,} registered samples")
    if st.button("↻ Refresh records", use_container_width=True):
        refresh_data()
        st.rerun()
    st.markdown("---")
    st.caption("SampleTrack · Quality & Laboratory")

# --------------------------- HEADER ---------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">QUALITY OPERATIONS · SAMPLE CONTROL</div>
        <h1>Sample & Location Tracking</h1>
        <p>A centralized workspace to register, locate, search and manage quality samples with a secure local SQLite database.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

df = st.session_state.samples_db.copy()
total = len(df)

# ============================================================
# 1. DASHBOARD
# ============================================================

if page == "Dashboard":
    page_title("Management Overview", "A live snapshot of your sample inventory and storage records.")
    underpad = int(df["Sample Type"].eq("Underpad Sample").sum()) if total else 0
    retention = int(df["Sample Type"].eq("Retention Sample").sum()) if total else 0
    evaluation = int(df["Sample Type"].eq("Evaluation Sample").sum()) if total else 0
    competitive = int(df["Sample Type"].eq("Competitive Sample").sum()) if total else 0

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        kpi_card("TOTAL SAMPLES", f"{total:,}", "📦", "#2563EB", "All registered records")
    with c2:
        kpi_card("UNDERPAD", f"{underpad:,}", "🧾", "#0F9D8A", "Underpad sample records")
    with c3:
        kpi_card("RETENTION", f"{retention:,}", "🔒", "#7657E8", "Retention sample records")
    with c4:
        kpi_card("EVALUATION", f"{evaluation:,}", "🧪", "#E69A2D", "Evaluation sample records")

    st.markdown('<div class="eyebrow">INVENTORY INSIGHTS</div>', unsafe_allow_html=True)
    if total:
        chart_col, location_col = st.columns([1.1, 1], gap="large")
        with chart_col:
            st.markdown("**Sample Type Distribution**")
            type_counts = (
                df["Sample Type"].value_counts()
                .reindex(SAMPLE_TYPES, fill_value=0)
                .rename_axis("Sample Type")
                .reset_index(name="Samples")
            )
            st.bar_chart(type_counts, x="Sample Type", y="Samples", use_container_width=True)
        with location_col:
            st.markdown("**Storage Location Distribution**")
            loc_counts = (
                df["Location"].value_counts()
                .rename_axis("Location")
                .reset_index(name="Samples")
            )
            st.bar_chart(loc_counts, x="Location", y="Samples", use_container_width=True)

        st.markdown('<div class="eyebrow">LATEST ACTIVITY</div>', unsafe_allow_html=True)
        st.markdown("**Recently Registered Samples**")
        for _, row in df.head(5).iterrows():
            display_sample(row)
    else:
        st.info("Your sample database is ready. Register your first sample to populate the dashboard.")

# ============================================================
# 2. SEARCH SAMPLES
# ============================================================

elif page == "Search Samples":
    page_title("Find a Sample", "Search by Sample ID, Lot Number, product, sample type or storage location.")
    search_col, type_col, location_col = st.columns([2, 1, 1], gap="medium")
    with search_col:
        query = st.text_input(
            "Keyword search",
            placeholder="Enter Sample ID, lot number or product...",
        )
    with type_col:
        selected_type = st.selectbox("Sample type", ["All types"] + SAMPLE_TYPES)
    with location_col:
        selected_location = st.selectbox("Storage location", ["All locations"] + LOCATIONS)

    results = df.copy()
    if query.strip():
        mask = results.astype(str).apply(
            lambda col: col.str.contains(query.strip(), case=False, na=False)
        ).any(axis=1)
        results = results[mask]
    if selected_type != "All types":
        results = results[results["Sample Type"] == selected_type]
    if selected_location != "All locations":
        results = results[results["Location"] == selected_location]

    st.markdown(
        f'<div class="eyebrow">SEARCH RESULTS · {len(results):,} RECORD(S)</div>',
        unsafe_allow_html=True,
    )
    if not results.empty:
        for _, row in results.iterrows():
            display_sample(row)
    elif total == 0:
        st.info("No samples have been registered yet.")
    else:
        st.warning("No matching samples found. Try a different keyword or filter.")

# ============================================================
# 3. REGISTER SAMPLE
# ============================================================

elif page == "Register Sample":
    page_title("Register New Sample", "Create a unique sample record and assign its storage location.")
    st.markdown("#### Sample information")
    st.caption("Fields marked with * are mandatory.")

    with st.form("register_sample_form", clear_on_submit=True):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            sample_id = st.text_input("Sample ID / Serial Number *", placeholder="e.g. SMP-2026-001")
            lot_number = st.text_input("Lot Number *", placeholder="Enter manufacturing lot number")
            sample_type = st.selectbox("Sample Type *", SAMPLE_TYPES)
        with col2:
            product_name = st.text_input("Product Name & Size", placeholder="e.g. Underpad 60 × 90 cm")
            location = st.selectbox("Storage Location / Rack *", LOCATIONS)
            image_path = st.text_input("Image URL or local image path", placeholder="Optional")

        st.markdown("---")
        submitted = st.form_submit_button(
            "💾  Save Sample Record",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not sample_id.strip() or not lot_number.strip():
                st.error("Sample ID and Lot Number are mandatory.")
            else:
                new_record = {
                    "Sample ID": sample_id.strip(),
                    "Lot Number": lot_number.strip(),
                    "Sample Type": sample_type,
                    "Product Name": product_name.strip(),
                    "Location": location,
                    "Image Path": image_path.strip(),
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                success, message = save_record(new_record)
                if success:
                    refresh_data()
                    st.success(f"Sample {sample_id.strip()} was successfully saved.")
                    st.toast("Sample registered successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error(message)

# ============================================================
# 4. SAMPLE DATABASE
# ============================================================

elif page == "Sample Database":
    page_title("Sample Database", "Review and export all registered sample records.")
    if not df.empty:
        top_left, top_right = st.columns([2, 1], gap="medium")
        with top_left:
            db_search = st.text_input("Filter database", placeholder="Search records...")
        with top_right:
            st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
            st.download_button(
                "⬇  Download CSV",
                data=df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"samples_database_{datetime.now():%Y%m%d}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        view_df = df.copy()
        if db_search.strip():
            mask = view_df.astype(str).apply(
                lambda col: col.str.contains(db_search.strip(), case=False, na=False)
            ).any(axis=1)
            view_df = view_df[mask]

        st.caption(f"Showing {len(view_df):,} of {len(df):,} records")
        st.dataframe(
            view_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Image Path": st.column_config.TextColumn("Image Path", width="medium"),
                "Sample ID": st.column_config.TextColumn("Sample ID", width="medium"),
                "Date": st.column_config.TextColumn("Registered Date", width="medium"),
            },
        )
    else:
        st.info("The database is currently empty. Register a sample to get started.")

# --------------------------- FOOTER --------------------------

st.markdown(
    """
    <div style="text-align:center;padding:28px 0 5px;color:#9AA7B8;font-size:10px;">
        SAMPLETRACK · QUALITY MANAGEMENT SYSTEM · POWERED BY SQLITE
    </div>
    """,
    unsafe_allow_html=True,
)
