import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

#app star
st.set_page_config(page_title="Online Course Dashboard", layout="wide")

# load data
@st.cache_data
def load_data():
    df = pd.read_csv("all_courses_clean.csv")

    # extract rating
    df["Rating_value"] = df["Rating"].astype(str).str.extract(r'(\d\.\d)')
    df["Rating_value"] = pd.to_numeric(df["Rating_value"], errors="coerce")

    # extract reviews
    df["Reviews_value"] = df["Rating"].astype(str).str.extract(r'\(([\d,]+)\)')
    df["Reviews_value"] = df["Reviews_value"].str.replace(",", "", regex=False)
    df["Reviews_value"] = pd.to_numeric(df["Reviews_value"], errors="coerce")

    # extract price
    df["Price_value"] = df["Price"].astype(str).str.extract(r'(\d+\.?\d*)')
    df["Price_value"] = pd.to_numeric(df["Price_value"], errors="coerce")

    # extract hours
    df["Hours"] = df["Details"].astype(str).str.extract(r'(\d+\.?\d*) total hours')
    df["Hours"] = pd.to_numeric(df["Hours"], errors="coerce")

    return df

df = load_data()

st.markdown("""
    <style>
    .main-title {
        font-size: 40px !important;
        color: #a2b7f3;
        font-weight: bold;
    }
    </style>
    <p class="main-title">Online Courses Dashboard</p>
    """, unsafe_allow_html=True)


# -------------------------------------------------
# Sidebar Filters & Branding
# -------------------------------------------------


# Create two columns inside the sidebar for the logos
side_col1, side_col2 = st.sidebar.columns(2)

with side_col1:
    # Fixed width of 60-80px usually fits sidebar best without crowding
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRiSwRvcOd97G2jgUrUYxtaexu5WKeZIu2Lug&s", width=70,use_container_width=True)
    
with side_col2:
    st.image("https://logowik.com/content/uploads/images/udemy-new-black2041.logowik.com.webp", width=70,use_container_width=True)

# Add a divider for visual clarity
st.sidebar.markdown("---")


st.sidebar.header("Filters")

# Platform Multi-select
platform_filter = st.sidebar.multiselect(
    "Select Platform",
    df["Platform"].unique(),
    default=df["Platform"].unique()
)

# Search Input
search = st.sidebar.text_input("Search Course")

# -------------------------------------------------
# Data Filtering Logic
# -------------------------------------------------
filtered = df[df["Platform"].isin(platform_filter)]

if search:
    filtered = filtered[filtered["Title"].str.contains(search, case=False, na=False)]





# -------------------------------------------------
# Statistics
# -------------------------------------------------

st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Courses", len(filtered))
col2.metric("Avg Rating", round(filtered["Rating_value"].mean(),2))
col3.metric("Avg Price", round(filtered["Price_value"].mean(),2))
col4.metric("Avg Duration (hours)", round(filtered["Hours"].mean(),2))

# -------------------------------------------------
# Charts
# -------------------------------------------------

st.subheader("Analysis")

col1, col2, col3 = st.columns(3)

# platform distribution
with col1:
    fig, ax = plt.subplots(figsize=(6,4))
    filtered["Platform"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Courses by Platform")
    st.pyplot(fig)

# rating distribution
with col2:
    fig, ax = plt.subplots(figsize=(6,4))
    filtered["Rating_value"].hist(bins=20, ax=ax)
    ax.set_title("Rating Distribution")
    st.pyplot(fig)

# Price distribution
with col3:
    fig, ax = plt.subplots(figsize=(6,4))
    filtered["Price_value"].hist(bins=20, ax=ax)
    ax.set_title("Price distribution")
    st.pyplot(fig)

# -------------------------------------------------
# Top Courses
# -------------------------------------------------

st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader("Top Reviewed Courses")

top_courses = filtered.sort_values(
    "Reviews_value", ascending=False
).head(5)

for i, (_, row) in enumerate(top_courses.iterrows(), start=1):

    st.markdown(f"""
        ##### {i}. {row['Title']}

        Platform: {row['Platform']}  
        Instructor/Partner: {row['Instructor_Partner']}  
        Rating: ⭐ {row['Rating_value']}  
        Reviews: {row['Reviews_value']}  
        """)

    st.divider()

# -------------------------------------------------
# Course Browser
# -------------------------------------------------

st.subheader("Browse Courses")

st.dataframe(
    filtered[[
        "Platform",
        "Title",
        "Instructor_Partner",
        "Rating_value",
        "Reviews_value",
        "Price_value",
        "Hours"
    ]],
    use_container_width=True
)