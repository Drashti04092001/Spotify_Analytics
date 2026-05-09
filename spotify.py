import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG
st.set_page_config(page_title="Spotify Dashboard", layout="wide")
st.title("Spotify Streaming Dashboard")

# LOAD DATA
def load_data():
    df = pd.read_csv("spotify_alltime_top100_songs.csv")

    df.columns = ["Rank","Track","Artist","Streams","Genre","BPM","Year",
                  "Country","Explicit","Danceability","Energy","Valence",
                  "Acousticness","Category"]

    return df

df = load_data()

#  SIDEBAR
st.sidebar.header(" Filters")

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (int(df["Year"].min()), int(df["Year"].max()))
)

genre = st.sidebar.multiselect("Genre", df["Genre"].unique())
artist = st.sidebar.multiselect("Artist", df["Artist"].unique())

top_n = st.sidebar.slider("Top N Songs", 1, 20, 5)

# HANDLE EMPTY FILTERS
if not genre:
    genre = df["Genre"].unique()

if not artist:
    artist = df["Artist"].unique()

#  FILTER DATA
filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1]) &
    (df["Genre"].isin(genre)) &
    (df["Artist"].isin(artist))
]

#  KPI
total_streams = filtered_df["Streams"].sum()
avg_streams = filtered_df["Streams"].mean()
total_tracks = filtered_df.shape[0]

previous_df = df[df["Year"] < year_range[0]]
previous_streams = previous_df["Streams"].sum()

growth = 0
if previous_streams > 0:
    growth = ((total_streams - previous_streams) / previous_streams) * 100

top_song = filtered_df.loc[filtered_df["Streams"].idxmax(), "Track"] if not filtered_df.empty else "N/A"
top_artist = filtered_df["Artist"].value_counts().idxmax() if not filtered_df.empty else "N/A"
avg_energy = filtered_df["Energy"].mean()
avg_dance = filtered_df["Danceability"].mean()
explicit_count = filtered_df["Explicit"].sum()

#  KPI DISPLAY
col1, col2, col3 = st.columns(3)

col1.metric(" Total Streams (B)", round(total_streams, 2), f"{round(growth, 2)}%")
col2.metric(" Average Streams", round(avg_streams, 2))
col3.metric(" Total Tracks", total_tracks)

st.markdown("---")

col4, col5, col6 = st.columns(3)
col4.metric(" Top Song", top_song)
col5.metric("Top Artist", top_artist)
col6.metric(" Avg Danceability", round(avg_dance, 2))

st.markdown("---")

#  TOP SONGS TABLE
st.subheader(f"Top {top_n} Songs by Streams")
top_songs = filtered_df.sort_values(by="Streams", ascending=False).head(top_n)
st.dataframe(top_songs, use_container_width=True)

st.markdown("---")

#  CHARTS

# 1. Streams Trend
st.subheader(" Streams Trend Over Years")
yearly = filtered_df.groupby("Year")["Streams"].sum().reset_index()

fig1 = px.line(yearly, x="Year", y="Streams", markers=True)
st.plotly_chart(fig1, use_container_width=True, key="chart1")

# 2. Top Artists
st.subheader(" Top Artists by Streams")
artist_df = filtered_df.groupby("Artist")["Streams"].sum().reset_index()
artist_df = artist_df.sort_values(by="Streams", ascending=False).head(10)

fig2 = px.bar(artist_df, x="Artist", y="Streams", text_auto=True)
st.plotly_chart(fig2, use_container_width=True, key="chart2")

# 3. Genre Distribution
st.subheader("Genre Distribution")
genre_df = filtered_df["Genre"].value_counts().reset_index()
genre_df.columns = ["Genre", "Count"]

fig3 = px.pie(genre_df, names="Genre", values="Count")
st.plotly_chart(fig3, use_container_width=True, key="chart3")

# 4. Danceability vs Energy
st.subheader("Danceability vs Energy")

fig4 = px.scatter(
    filtered_df,
    x="Danceability",
    y="Energy",
    size="Streams",
    color="Genre",
    hover_data=["Track", "Artist"]
)

st.plotly_chart(fig4, use_container_width=True, key="chart4")

# 5. Explicit Content
st.subheader("Explicit vs Non-Explicit")
explicit_df = filtered_df["Explicit"].value_counts().reset_index()
explicit_df.columns = ["Type", "Count"]

fig5 = px.pie(explicit_df, names="Type", values="Count", hole=0.4)
st.plotly_chart(fig5, use_container_width=True, key="chart5")

# 6. BPM Distribution
st.subheader(" BPM Distribution")
fig6 = px.histogram(filtered_df, x="BPM", nbins=20)
st.plotly_chart(fig6, use_container_width=True, key="chart6")

# FOOTER
st.markdown("---")
st.caption(" Spotify Dashboard | Built with Streamlit & Plotly")