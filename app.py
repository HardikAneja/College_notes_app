# import streamlit as st
# import pandas as pd

# @st.cache_data
# def load_data():
#     return pd.read_csv("notes_content_template.csv")

# data = load_data()

# st.title("📚 College Notes Hub")

# course = st.selectbox("Select Course", sorted(data['Course'].unique()))
# filtered_data = data[data['Course'] == course]

# semester = st.selectbox("Select Semester", sorted(filtered_data['Semester'].unique()))
# filtered_data = filtered_data[filtered_data['Semester'] == semester]

# subject = st.selectbox("Select Subject", sorted(filtered_data['Subject'].unique()))
# filtered_data = filtered_data[filtered_data['Subject'] == subject]

# st.subheader(f"Notes for {subject}")

# for _, row in filtered_data.iterrows():
#     st.markdown(f"### {row['Unit']}: {row['Topic']}")
#     st.markdown(f"[📥 Download Notes]({row['Notes_Link']})")