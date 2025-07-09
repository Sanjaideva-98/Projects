import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load dataset
df = pd.read_csv("D:/imdb_2024_all_genres.csv")

st.set_page_config(layout="wide", page_title="IMDb 2024 Dashboard")
st.title("IMDb 2024 Movies Data Dashboard")

st.sidebar.header("Filter Options")

# Genre filter
selected_genres = st.sidebar.multiselect("Select Genres", options=df["Genre"].unique(), default=df["Genre"].unique())

# Duration filter
duration_filter = st.sidebar.selectbox("Select Duration Range (in hours)", ["All", "< 2 hrs", "2-3 hrs", "> 3 hrs"])
if duration_filter == "< 2 hrs":
    df = df[df["Duration"] < 120]
elif duration_filter == "2-3 hrs":
    df = df[(df["Duration"] >= 120) & (df["Duration"] <= 180)]
elif duration_filter == "> 3 hrs":
    df = df[df["Duration"] > 180]

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating", min_value=float(df["Rating"].min()), max_value=float(df["Rating"].max()), value=0.0)
df = df[df["Rating"] >= min_rating]

# Voting filter
min_votes = st.sidebar.number_input("Minimum Votes", min_value=0, value=0, step=1000)
df = df[df["Votes"] >= min_votes]

# Apply genre filter
filtered_df = df[df["Genre"].isin(selected_genres)]

# Display filtered dataset
st.subheader("Filtered Results")
st.dataframe(filtered_df)

# Top 10 Movies by Rating and Voting Counts
st.subheader("Top 10 Movies by Rating and Voting Counts")
top_10 = filtered_df.sort_values(by=["Rating", "Votes"], ascending=[False, False]).head(10)
st.dataframe(top_10[["Title", "Genre", "Rating", "Votes"]])

# Genre Distribution
st.subheader("Genre Distribution")
genre_count = filtered_df["Genre"].value_counts()
fig1 = px.bar(genre_count, x=genre_count.index, y=genre_count.values, labels={"x": "Genre", "y": "Number of Movies"}, color=genre_count.index)
st.plotly_chart(fig1)

# Average Duration by Genre
st.subheader("Average Duration by Genre")
avg_duration = filtered_df.groupby("Genre")["Duration"].mean().sort_values()
fig2 = px.bar(avg_duration, orientation='h', labels={"value": "Average Duration (mins)", "index": "Genre"})
st.plotly_chart(fig2)

# Voting Trends by Genre
st.subheader("Average Votes by Genre")
avg_votes = filtered_df.groupby("Genre")["Votes"].mean().sort_values(ascending=False)
fig3 = px.bar(avg_votes, labels={"value": "Average Votes", "index": "Genre"}, color=avg_votes.index)
st.plotly_chart(fig3)

# Rating Distribution
st.subheader("Rating Distribution")
fig4, ax1 = plt.subplots()
sns.histplot(filtered_df["Rating"], bins=10, kde=True, ax=ax1)
st.pyplot(fig4)

# Genre-Based Rating Leaders
st.subheader("Top Rated Movie in Each Genre")
idx = filtered_df.groupby("Genre")["Rating"].idxmax()
leaders = filtered_df.loc[idx][["Genre", "Title", "Rating", "Votes"]].sort_values(by="Rating", ascending=False)
st.dataframe(leaders)

# Most Popular Genres by Total Votes
st.subheader("Most Popular Genres by Total Voting")
genre_votes = filtered_df.groupby("Genre")["Votes"].sum()
fig5 = px.pie(values=genre_votes.values, names=genre_votes.index, title="Total Votes by Genre")
st.plotly_chart(fig5)

# Duration Extremes
st.subheader("Shortest and Longest Movies")
shortest = filtered_df.loc[filtered_df["Duration"].idxmin()]
longest = filtered_df.loc[filtered_df["Duration"].idxmax()]

col1, col2 = st.columns(2)
with col1:
    st.metric("Shortest Movie", f"{shortest['Title']} ({shortest['Duration']} mins)")
with col2:
    st.metric("Longest Movie", f"{longest['Title']} ({longest['Duration']} mins)")

# Ratings by Genre - Heatmap
st.subheader("Ratings by Genre (Heatmap)")
pivot = filtered_df.pivot_table(index="Genre", values="Rating", aggfunc="mean")
fig6, ax2 = plt.subplots(figsize=(8, 5))
sns.heatmap(pivot, annot=True, cmap="YlGnBu", ax=ax2)
st.pyplot(fig6)

# Correlation Analysis: Rating vs Votes
st.subheader("Correlation: Rating vs Votes")
fig7 = px.scatter(filtered_df, x="Votes", y="Rating", hover_data=["Title"], trendline="ols")
st.plotly_chart(fig7)
