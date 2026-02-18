import streamlit as st
from datetime import date
from country_tracker.data import DataLoader
from country_tracker.models import TravelEntry, Document

st.set_page_config(page_title="Data Entry", page_icon="📝")

st.title("📝 Data Entry")

data_loader = DataLoader()

tab1, tab2 = st.tabs(["Add Travel", "Add Document"])

with tab1:
    st.header("Add Travel Entry")
    with st.form("travel_form"):
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start Date", value=date.today())
        end_date = col2.date_input("End Date", value=date.today())

        col3, col4 = st.columns(2)
        country = col3.text_input("Country")
        iso3 = col4.text_input("ISO3 Code (Optional)")

        notes = st.text_area("Notes (Optional)")

        submitted = st.form_submit_button("Add Travel")

        if submitted:
            if not country:
                st.error("Country is required.")
            elif end_date < start_date:
                st.error("End date must be after start date.")
            else:
                entry = TravelEntry(
                    start_date=start_date,
                    end_date=end_date,
                    country=country,
                    iso3=iso3 if iso3 else None,
                    notes=notes if notes else None,
                )
                try:
                    data_loader.append_travel_entry(entry)
                    st.success(f"Added travel to {country}!")
                except Exception as e:
                    st.error(f"Error saving: {e}")

with tab2:
    st.header("Add Document")
    with st.form("doc_form"):
        col1, col2 = st.columns(2)
        doc_type = col1.selectbox("Type", ["passport", "visa"])
        country = col2.text_input("Country/Region")

        name = st.text_input("Name (e.g. US B1/B2)")

        col3, col4 = st.columns(2)
        issue_date = col3.date_input("Issue Date", value=date.today())
        expiry_date = col4.date_input("Expiry Date", value=date.today())

        st.subheader("Rules (Optional)")
        col5, col6, col7 = st.columns(3)
        max_days = col5.number_input("Max Days", min_value=0, value=None, step=1)
        window_days = col6.number_input("Window Days", min_value=0, value=None, step=1)
        renew_before = col7.number_input(
            "Renew Before (Days)", min_value=0, value=None, step=1
        )

        notes = st.text_area("Notes (Optional)")

        submitted = st.form_submit_button("Add Document")

        if submitted:
            if not country or not name:
                st.error("Country and Name are required.")
            elif expiry_date < issue_date:
                st.error("Expiry date must be after issue date.")
            else:
                # Handle 0 as None for optional number inputs if streamlit returns 0 for empty?
                # Streamlit number_input with value=None returns None if not changed?
                # Actually value=None is not supported for int.
                # Let's assume user leaves it as 0 if not applicable, but I set min_value=0.
                # If I want optional, I might need text_input and convert, or use 0 as "N/A".
                # For now, let's assume 0 means N/A for max_days/window_days.

                doc = Document(
                    doc_type=doc_type,
                    country=country,
                    name=name,
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    max_days=int(max_days) if max_days else None,
                    window_days=int(window_days) if window_days else None,
                    renew_before_days=int(renew_before) if renew_before else None,
                    notes=notes if notes else None,
                )
                try:
                    data_loader.append_document(doc)
                    st.success(f"Added document {name}!")
                except Exception as e:
                    st.error(f"Error saving: {e}")
