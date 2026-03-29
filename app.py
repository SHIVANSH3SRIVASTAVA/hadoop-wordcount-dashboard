import streamlit as st
import subprocess
import os
import pandas as pd

st.set_page_config(page_title="Hadoop WordCount", layout="centered")

# -------------------- DARK THEME (FORCED) --------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }

    /* Text */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: white !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #444;
        padding: 0.5rem 1rem;
    }

    /* File uploader */
    .stFileUploader {
        background-color: #1c1e26;
        color: white;
        border-radius: 10px;
        padding: 10px;
    }

    /* Dataframe */
    .stDataFrame {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.title("📊 Hadoop WordCount Dashboard")
st.markdown("---")

# -------------------- SESSION STATE --------------------
if "data_ready" not in st.session_state:
    st.session_state.data_ready = False

if "show_top" not in st.session_state:
    st.session_state.show_top = False

if "show_chart" not in st.session_state:
    st.session_state.show_chart = False

# -------------------- FILE UPLOAD --------------------
st.subheader("📂 Upload Input File")

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])

if uploaded_file is not None:
    with open("input/user_input.txt", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("✅ File uploaded successfully!")

    if st.button("🚀 Run WordCount"):

        st.session_state.data_ready = False
        st.session_state.show_top = False
        st.session_state.show_chart = False

        if os.path.exists("output"):
            subprocess.run(["rm", "-rf", "output"])

        with st.spinner("Processing with Hadoop..."):
            subprocess.run(
                ["bash", "run.sh", "input/user_input.txt"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        st.session_state.data_ready = True

# -------------------- RESULTS --------------------
if st.session_state.data_ready:

    if os.path.exists("output/part-r-00000"):

        df = pd.read_csv("output/part-r-00000", sep="\t", header=None)
        df.columns = ["Word", "Count"]

        df_sorted = df.sort_values(by="Count", ascending=False).reset_index(drop=True)

        # -------------------- FULL OUTPUT --------------------
        st.subheader("📄 Full Word Count Output")

        search_query = st.text_input("🔍 Search word")

        if search_query:
            filtered_df = df_sorted[
                df_sorted["Word"].str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_df = df_sorted

        st.dataframe(filtered_df, hide_index=True, width="stretch")

        st.markdown("---")

        # -------------------- ANALYSIS --------------------
        st.subheader("⚙️ Analysis Tools")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📈 Toggle Top Words"):
                st.session_state.show_top = not st.session_state.show_top

        with col2:
            if st.button("📊 Toggle Chart"):
                st.session_state.show_chart = not st.session_state.show_chart

        # -------------------- TOP WORDS --------------------
        if st.session_state.show_top:
            st.subheader("🔝 Top 5 Words")
            st.table(df_sorted.head(5))

        # -------------------- CHART --------------------
        if st.session_state.show_chart:
            st.subheader("📊 Word Frequency Chart")
            st.bar_chart(df_sorted.head(5).set_index("Word"))

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Built with ❤️ using Hadoop + Streamlit")
