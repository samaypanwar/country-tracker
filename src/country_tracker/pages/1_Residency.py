import streamlit as st
import pandas as pd
from datetime import date
from country_tracker.data import DataLoader
from country_tracker.services import expand_travel_dates, calculate_residency

st.set_page_config(page_title="Residency Details", page_icon="🏠")

st.title("🏠 Residency Details")

data_loader = DataLoader()
travel_log = data_loader.load_travel_log()
daily_df = expand_travel_dates(travel_log)

if daily_df.empty:
    st.warning("No travel data found.")
else:
    # Select Country
    countries = sorted(daily_df["country"].unique())
    selected_country = st.selectbox("Select Country", countries)

    today = date.today()

    # Calculate stats
    d183 = calculate_residency(daily_df, selected_country, 183, today)
    d365 = calculate_residency(daily_df, selected_country, 365, today)

    col1, col2 = st.columns(2)
    col1.metric("Days in Last 183 Days", d183)
    col2.metric("Days in Last 365 Days", d365)

    # Rolling Window Plot
    st.subheader(f"Rolling 183-Day Count for {selected_country}")

    # Calculate rolling count for the last year
    dates = pd.date_range(end=today, periods=365)
    rolling_counts = []
    for d in dates:
        count = calculate_residency(daily_df, selected_country, 183, d.date())
        rolling_counts.append({"Date": d, "Days": count})

    rolling_df = pd.DataFrame(rolling_counts).set_index("Date")
    st.line_chart(rolling_df)

    # Yearly Breakdown
    st.subheader("Yearly Breakdown")
    # Group by year
    daily_df["year"] = daily_df.index.year
    yearly_counts = (
        daily_df[daily_df["country"] == selected_country].groupby("year").size()
    )
    st.bar_chart(yearly_counts)
