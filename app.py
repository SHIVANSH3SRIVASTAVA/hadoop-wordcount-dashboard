import streamlit as st
import subprocess
import os
import pandas as pd
import re

st.set_page_config(page_title="Hadoop WordCount", layout="centered")

# -------------------- CONFIG --------------------
DEPLOY_MODE = True   # 👉 Change to False for local Hadoop execution

# -------------------- DARK THEME --------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: white !important;
    }
    .stButton>button {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #444;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.title("📊 Hadoop WordCount Dashboard")
st.markdown("---")

# -------------------- SESSION STATE --------------------
if "data_ready" not in st.session_state:
    st.session_state.data_ready = False

if "df_sorted" not in st.session_state:
    st.session_state.df_sorted = None

# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])

if uploaded_file is not None:

    text = uploaded_file.read().decode("utf-8")
    st.success("✅ File uploaded successfully!")

    if st.button("🚀 Run WordCount"):

        st.session_state.data_ready = False

        # -------------------- DEPLOY MODE --------------------
        if DEPLOY_MODE:
            words = re.findall(r"[a-zA-Z]+", text.lower())

            word_count = {}
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1

            df = pd.DataFrame(word_count.items(), columns=["Word", "Count"])
            df_sorted = df.sort_values(by="Count", ascending=False).reset_index(drop=True)

        # -------------------- HADOOP MODE --------------------
        else:
            with open("input/user_input.txt", "w") as f:
                f.write(text)

            if os.path.exists("output"):
                subprocess.run(["rm", "-rf", "output"])

            subprocess.run(
                ["bash", "run.sh", "input/user_input.txt"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            df = pd.read_csv("output/part-r-00000", sep="\t", header=None)
            df.columns = ["Word", "Count"]

            df_sorted = df.sort_values(by="Count", ascending=False).reset_index(drop=True)

        # Save to session
        st.session_state.df_sorted = df_sorted
        st.session_state.data_ready = True

# -------------------- RESULTS --------------------
if st.session_state.data_ready:

    df_sorted = st.session_state.df_sorted

    st.subheader("📄 Full Word Count Output")

    # 🔍 Search
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
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Show Top Words"):
            st.table(df_sorted.head(5))

    with col2:
        if st.button("📊 Show Chart"):
            st.bar_chart(df_sorted.head(5).set_index("Word"))

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Hadoop (Local) + Deployable UI Version")
