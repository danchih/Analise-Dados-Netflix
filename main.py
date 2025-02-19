import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px

# Answer the Questions:
#     - How many titles (movies and TV shows) are available in the dataset?
#     - What is the ratio of movies to TV shows in the catalog?
#     - What is the average duration of the Movies and TV Shows?
#     - Which countries produced the most titles in the catalog?"
#     - What is the most common rating in the catalog?

# Date Selection -----------------------------------------------------------------------------
df = pd.read_csv("netflix_titles.csv")      

print(df.shape)     # (8807, 12)
df.info()

# Removing unnecessary columns
del df['show_id']
del df['date_added']

# Check and clear the null objects
null_values = df.isnull().sum().sort_values(ascending=False)
print(null_values)
df = df.dropna() 
df["country"] = df["country"].str.strip().str.lstrip(',')

# Check the duplicate values
print("\n Duplicated Values: \n", df.duplicated().value_counts())


# SideBar ---------------------------------------------------------------------------------------------
st.set_page_config(layout="wide")

year_options = ["None"] + sorted(df["release_year"].unique(), reverse=True)
year = st.sidebar.selectbox("Release Year", year_options)

df_gender = df['listed_in'].str.split(',').explode().str.strip()
gender_options = sorted(df_gender.unique())
gender = st.sidebar.multiselect("Movie/TV Show Gender", gender_options)

df_countries = df["country"].str.split(',').explode().str.strip()
country_options = sorted(df_countries.unique())
country = st.sidebar.multiselect("Select the Country", country_options)

type_options = ["None"] + list(df["type"].unique())
movie = st.sidebar.checkbox("Movies")
tv_show = st.sidebar.checkbox("TV Shows")

if year == "None" and gender == "None" and country == "None" and not movie and not tv_show:
    df_filtered = df
else:
    df_filtered = df
    if year != "None":
        df_filtered = df_filtered[df_filtered["release_year"] == year]
    if gender:
        df_filtered = df_filtered[df_filtered["listed_in"].apply(lambda x: any(g in x for g in gender))]
    if country:
        df_filtered = df_filtered[df_filtered["country"].apply(lambda x: any(c in x for c in country))]

    if movie and tv_show:
        df.filtered = df_filtered[df_filtered["type"].str.lower().isin(["movie", "tv show"])]
    elif movie:
        df_filtered = df_filtered[df_filtered["type"].str.lower() == "movie"]
    elif tv_show:
        df_filtered = df_filtered[df_filtered["type"].str.lower() == "tv show"]

st.sidebar.link_button("Link to Dataset", "https://www.kaggle.com/datasets/anandshaw2001/netflix-movies-and-tv-shows")


# Page -------------------------------------------------------------------------------------

st.title("Dashboard Netflix")

col1, col2, col3, col4 = st.columns(4)
col5, col6 = st.columns(2)
col7, col8 = st.columns(2)

# Counting only different types
df_types_filtered = df_filtered['type'].str.strip().str.lower().value_counts().reset_index()
df_types_filtered.columns = ['Type', 'Total']

df_rating_filtered = df_filtered['rating'].str.strip().value_counts().reset_index()
df_rating_filtered.columns = ['Rating', 'Total']

df_country_filtered = df_filtered.groupby(['country', 'release_year']).size().reset_index(name='Total')
df_country_filtered.columns = ['Country', 'Release Year', 'Total']

# Convert the type object to int (calculating the average duration)
duration_filtered = df_filtered['duration'].str.strip()
duration_min_filtered = duration_filtered[duration_filtered.str.contains('min', regex=True)]
duration_min_filtered = duration_min_filtered.str.replace('min', '', regex=True).astype(int)

duration_season_filtered = duration_filtered[duration_filtered.str.contains('Season(s)?', regex=True)]
duration_season_filtered = duration_season_filtered.str.replace('Season(s)?', '', regex=True).astype(int)


with col1:
    st.metric(label="Movies", value=(df_types_filtered[df_types_filtered['Type'] == 'movie']['Total'].iloc[0]) if 'movie' in df_types_filtered['Type'].values else 0)

with col2:
    st.metric(label="Average Duration of Movies (min)", value=duration_min_filtered.mean().round(2) if len(duration_min_filtered) > 0 else 0)

with col3: 
    st.metric(label="TV Show", value=df_types_filtered[df_types_filtered['Type'] == 'tv show']['Total'].iloc[0] if 'tv show' in df_types_filtered['Type'].values else 0)

with col4: 
    st.metric(label="Average Duration of TV Shows (Seasons)", value=duration_season_filtered.mean().round(2) if len(duration_season_filtered) > 0 else 0)

# Grafics
fig = px.pie(df_types_filtered, values='Total', names='Type', title="Distribution of Content on Netflix", hole=0.4)  
col5.plotly_chart(fig, use_container_width=True)

fig_rating = px.pie(df_rating_filtered, values='Total', names="Rating", title="Rating")
col6.plotly_chart(fig_rating, use_container_width=True)

st.subheader("Total Number of Titles Released by Country in each Year")
st.bar_chart(df_country_filtered, x="Release Year", y="Total", color="Country", stack=False, use_container_width=True)


# Table
st.subheader("Table with All the Information")
st.write(df_filtered)


