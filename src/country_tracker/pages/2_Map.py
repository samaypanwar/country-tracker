import streamlit as st
import pandas as pd
from country_tracker.data import DataLoader
from country_tracker.services import expand_travel_dates
from country_tracker.visualization import create_world_map

st.set_page_config(page_title="World Map", page_icon="🌍")

st.title("🌍 World Map Heatmap")

data_loader = DataLoader()
travel_log = data_loader.load_travel_log()
daily_df = expand_travel_dates(travel_log)

if daily_df.empty:
    st.warning("No travel data found.")
else:
    # Filter by Year
    years = sorted(daily_df.index.year.unique(), reverse=True)

    # Multiselect for years
    selected_years = st.multiselect("Select Years (Leave empty for All Time)", years)

    # Filter data based on selection
    if not selected_years:
        # If empty, show all data
        filtered_df = daily_df
        display_title = "All Time"
    else:
        # Filter for selected years
        filtered_df = daily_df[daily_df.index.year.isin(selected_years)]
        display_title = ", ".join(map(str, sorted(selected_years)))

    # Group by country/iso3 and count days
    country_counts = (
        filtered_df.groupby(["country", "iso3"]).size().reset_index(name="days")
    )

    if country_counts.empty:
        st.warning(f"No travel data for {display_title}.")
    else:
        # Map Options
        col1, col2 = st.columns(2)
        projection_type = col1.selectbox(
            "Projection",
            ["natural earth", "orthographic", "mercator", "equirectangular"],
        )
        color_scale_name = col2.selectbox(
            "Color Scale", ["Blues", "Plasma", "Viridis", "Inferno", "Turbo", "RdBu"]
        )

        # Create Map
        fig = create_world_map(
            country_counts, projection=projection_type, color_scale=color_scale_name
        )

        # Update title
        fig.update_layout(title=f"Days Spent per Country ({display_title})")

        st.plotly_chart(fig, use_container_width=True)
