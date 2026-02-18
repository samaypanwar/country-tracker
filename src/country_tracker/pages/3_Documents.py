import streamlit as st
import pandas as pd
from datetime import date
from country_tracker.data import DataLoader
from country_tracker.services import expand_travel_dates, check_compliance

st.set_page_config(page_title="Documents", page_icon="📄")

st.title("📄 Documents & Visa Compliance")

data_loader = DataLoader()
travel_log = data_loader.load_travel_log()
documents = data_loader.load_documents()

if not documents:
    st.warning("No documents found. Please add data.")
else:
    daily_df = expand_travel_dates(travel_log)

    # Check Compliance
    today = date.today()
    compliance_results = check_compliance(documents, daily_df, reference_date=today)

    # Display Results
    for res in compliance_results:
        status_color = {
            "ok": "green",
            "warning": "orange",
            "violation": "red",
            "expired": "grey",
        }.get(res["status"], "black")

        with st.container():
            st.markdown(f"### {res['document']} ({res['country']})")
            st.markdown(f"**Status:** :{status_color}[{res['status'].upper()}]")
            st.markdown(f"**Message:** {res['message']}")

            if res["days_used"] is not None:
                st.progress(
                    min(
                        res["days_used"]
                        / (
                            res["days_used"] + res["days_remaining"]
                            if res["days_remaining"] is not None
                            else 100
                        ),
                        1.0,
                    )
                )
                st.caption(
                    f"{res['days_used']} days used / {res['days_remaining']} days remaining"
                )

            st.divider()
