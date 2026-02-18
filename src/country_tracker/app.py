import streamlit as st
import pandas as pd
from datetime import date, timedelta
from country_tracker.data import DataLoader
from country_tracker.services import expand_travel_dates, calculate_residency

st.set_page_config(page_title="Residency Tracker", page_icon="🌍", layout="wide")

st.title("🌍 Residency + Visa Tracker")

# Load Data
data_loader = DataLoader()
travel_log = data_loader.load_travel_log()
documents = data_loader.load_documents()

if not travel_log:
    st.warning("No travel log found. Please add data.")
else:
    # Process Data
    daily_df = expand_travel_dates(travel_log)

    # Overview Metrics
    st.header("Where am I now?")

    today = date.today()

    # Find current location
    # Check if today is in daily_df
    current_loc = "Unknown"
    if pd.Timestamp(today) in daily_df.index:
        current_loc = daily_df.loc[pd.Timestamp(today), "country"]
    else:
        # Check if we have future plans or if we are just "somewhere" not logged
        # Or maybe the last known location?
        if not daily_df.empty:
            last_date = daily_df.index.max().date()
            if last_date < today:
                last_loc = daily_df.loc[pd.Timestamp(last_date), "country"]
                current_loc = f"{last_loc} (Last known on {last_date})"
            else:
                # Future?
                pass

    st.metric("Current Location", current_loc)

    # Rolling Window Presence
    st.subheader("Rolling Window Presence")

    col1, col2, col3 = st.columns(3)

    # We need to know which country to show. Maybe the current one?
    # Or let user select.
    # For Overview, let's show "Top Countries"

    # Calculate days in last 365 days for all countries
    # This is a bit inefficient to loop all countries, but fine for MVP
    countries = daily_df["country"].unique()

    residency_stats = []
    for c in countries:
        d183 = calculate_residency(daily_df, c, 183, today)
        d365 = calculate_residency(daily_df, c, 365, today)
        residency_stats.append(
            {"Country": c, "Last 183 Days": d183, "Last 365 Days": d365}
        )

    stats_df = pd.DataFrame(residency_stats).sort_values(
        "Last 365 Days", ascending=False
    )

    st.dataframe(stats_df, hide_index=True)

    # Top Countries Chart
    st.subheader("Top Countries (Last 365 Days)")
    st.bar_chart(stats_df.set_index("Country")["Last 365 Days"])
