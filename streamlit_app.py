import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Global Weather Dashboard",
    page_icon="🌦️",
    layout="wide",
)

database_path = Path(__file__).resolve().parent / "weather.db"


@st.cache_data
def load_weather_data():
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(
            """
            SELECT
                City,
                Country,
                Local_Time,
                Temperature,
                Temperature_F
            FROM weather_clean
            """,
            connection,
        )


st.title("Global Weather Dashboard")
st.write(
    "Explore a scraped snapshot of temperatures from cities around the world. "
    "Use the sidebar filters to update the dashboard."
)

if not database_path.exists():
    st.error("The weather.db database could not be found.")
    st.stop()

try:
    weather = load_weather_data()
except sqlite3.Error as error:
    st.error(f"The weather database could not be read: {error}")
    st.stop()

weather["Temperature_F"] = pd.to_numeric(
    weather["Temperature_F"],
    errors="coerce",
)
weather = weather.dropna(subset=["Temperature_F"])

countries = sorted(weather["Country"].unique())

st.sidebar.header("Dashboard Filters")

selected_countries = st.sidebar.multiselect(
    "Select countries",
    options=countries,
    default=countries,
)

minimum_temperature = int(weather["Temperature_F"].min())
maximum_temperature = int(weather["Temperature_F"].max())

selected_temperature_range = st.sidebar.slider(
    "Temperature range (°F)",
    min_value=minimum_temperature,
    max_value=maximum_temperature,
    value=(minimum_temperature, maximum_temperature),
)

ranking = st.sidebar.radio(
    "City ranking",
    options=["Warmest", "Coolest"],
)

top_city_count = st.sidebar.slider(
    "Number of cities to display",
    min_value=5,
    max_value=20,
    value=10,
)

if not selected_countries:
    st.warning("Select at least one country to display the dashboard.")
    st.stop()

filtered_weather = weather[
    weather["Country"].isin(selected_countries)
    & weather["Temperature_F"].between(
        selected_temperature_range[0],
        selected_temperature_range[1],
    )
].copy()

if filtered_weather.empty:
    st.warning("No cities match the selected filters.")
    st.stop()

city_count = filtered_weather["City"].nunique()
country_count = filtered_weather["Country"].nunique()
average_temperature = filtered_weather["Temperature_F"].mean()
lowest_temperature = filtered_weather["Temperature_F"].min()
highest_temperature = filtered_weather["Temperature_F"].max()

metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)

metric_1.metric("Cities", city_count)
metric_2.metric("Countries", country_count)
metric_3.metric("Average", f"{average_temperature:.1f} °F")
metric_4.metric("Lowest", f"{lowest_temperature:.0f} °F")
metric_5.metric("Highest", f"{highest_temperature:.0f} °F")

st.subheader("Average Temperature by Country")
st.write(
    "The map compares the average temperature of the cities included "
    "for each country."
)

country_summary = (
    filtered_weather.groupby("Country", as_index=False)
    .agg(
        Average_Temperature=("Temperature_F", "mean"),
        City_Count=("City", "nunique"),
    )
)

map_figure = px.choropleth(
    country_summary,
    locations="Country",
    locationmode="country names",
    color="Average_Temperature",
    hover_name="Country",
    hover_data={
        "Average_Temperature": ":.1f",
        "City_Count": True,
    },
    color_continuous_scale="RdYlBu_r",
    labels={
        "Average_Temperature": "Average Temperature (°F)",
        "City_Count": "Cities",
    },
)

map_figure.update_layout(
    margin={"r": 0, "t": 10, "l": 0, "b": 0},
)

st.plotly_chart(map_figure, use_container_width=True)

left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Temperature Distribution")
    st.write("This histogram shows how city temperatures are distributed.")

    histogram_figure = px.histogram(
        filtered_weather,
        x="Temperature_F",
        nbins=15,
        color_discrete_sequence=["#3b82f6"],
        labels={
            "Temperature_F": "Temperature (°F)",
            "count": "Number of Cities",
        },
    )

    histogram_figure.update_layout(
        yaxis_title="Number of Cities",
        showlegend=False,
    )

    st.plotly_chart(histogram_figure, use_container_width=True)

with right_column:
    st.subheader(f"{ranking} Cities")
    st.write(
        f"This chart shows the {top_city_count} {ranking.lower()} cities "
        "that match the current filters."
    )

    show_coolest_first = ranking == "Coolest"

    ranked_cities = (
        filtered_weather.sort_values(
            "Temperature_F",
            ascending=show_coolest_first,
        )
        .head(top_city_count)
        .sort_values("Temperature_F")
    )

    bar_figure = px.bar(
        ranked_cities,
        x="Temperature_F",
        y="City",
        orientation="h",
        color="Temperature_F",
        hover_data=["Country", "Local_Time"],
        color_continuous_scale="RdYlBu_r",
        labels={
            "Temperature_F": "Temperature (°F)",
            "City": "City",
            "Country": "Country",
            "Local_Time": "Local Time",
        },
    )

    bar_figure.update_layout(coloraxis_showscale=False)

    st.plotly_chart(bar_figure, use_container_width=True)

with st.expander("View Filtered Weather Data"):
    st.dataframe(
        filtered_weather.sort_values(
            "Temperature_F",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )