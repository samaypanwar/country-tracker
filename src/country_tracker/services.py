import pandas as pd
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from country_tracker.models import TravelEntry, Document, ResidencyStatus


def expand_travel_dates(entries: List[TravelEntry]) -> pd.DataFrame:
    """
    Expands a list of TravelEntry objects into a daily DataFrame.
    Index: date
    Columns: country, iso3, notes

    Later entries overwrite earlier ones in case of overlap.
    """
    if not entries:
        return pd.DataFrame(columns=["country", "iso3", "notes"])

    # Create a list of daily records
    daily_records = []

    # Sort entries by start_date to ensure consistent overwriting behavior
    sorted_entries = sorted(entries, key=lambda x: x.start_date)

    for entry in sorted_entries:
        # Generate date range for this entry
        # inclusive of both start and end date
        current_date = entry.start_date

        # Handle missing end_date (e.g., current stay)
        end_date = entry.end_date
        if pd.isna(end_date):
            end_date = date.today()

        while current_date <= end_date:
            daily_records.append(
                {
                    "date": pd.Timestamp(current_date),
                    "country": entry.country,
                    "iso3": entry.iso3,
                    "notes": entry.notes,
                }
            )
            current_date += timedelta(days=1)

    if not daily_records:
        return pd.DataFrame(columns=["country", "iso3", "notes"])

    # Create DataFrame
    df = pd.DataFrame(daily_records)

    # Set index to date
    df.set_index("date", inplace=True)

    # Handle duplicates (overlaps) by keeping the last one
    df = df[~df.index.duplicated(keep="last")]

    return df.sort_index()


def calculate_residency(
    daily_df: pd.DataFrame,
    country: str,
    window_days: int,
    reference_date: date = date.today(),
) -> int:
    """
    Calculates the number of days spent in 'country' within the last 'window_days'
    ending on 'reference_date' (inclusive).
    """
    if daily_df.empty:
        return 0

    ref_ts = pd.Timestamp(reference_date)
    start_ts = ref_ts - pd.Timedelta(days=window_days - 1)  # window includes today

    # Filter for dates within the window
    mask = (daily_df.index >= start_ts) & (daily_df.index <= ref_ts)
    window_df = daily_df.loc[mask]

    # Count occurrences of the country
    # We need to handle potential case sensitivity, but for now exact match
    count = window_df[window_df["country"] == country].shape[0]

    return count


def check_compliance(
    documents: List[Document],
    daily_df: pd.DataFrame,
    reference_date: date = date.today(),
) -> List[Dict[str, Any]]:
    results = []

    for doc in documents:
        status = {
            "document": doc.name,
            "country": doc.country,
            "status": "ok",
            "message": "",
            "days_used": 0,
            "days_remaining": None,
        }

        # 1. Check Expiry
        days_until_expiry = (doc.expiry_date - reference_date).days

        if days_until_expiry < 0:
            status["status"] = "expired"
            status["message"] = f"Expired {abs(days_until_expiry)} days ago"
        elif doc.renew_before_days and days_until_expiry <= doc.renew_before_days:
            status["status"] = "warning"
            status["message"] = (
                f"Expires in {days_until_expiry} days (Renew by {doc.expiry_date - timedelta(days=doc.renew_before_days)})"
            )
        else:
            status["message"] = f"Expires in {days_until_expiry} days"

        # 2. Check Rolling Window (e.g. 90/180)
        if doc.max_days and doc.window_days:
            days_used = calculate_residency(
                daily_df, doc.country, doc.window_days, reference_date
            )
            status["days_used"] = days_used
            status["days_remaining"] = doc.max_days - days_used

            if days_used > doc.max_days:
                status["status"] = "violation"
                status["message"] += (
                    f" | Overstayed: {days_used}/{doc.max_days} days in last {doc.window_days} days"
                )
            elif days_used >= (doc.max_days - 10):  # Warning threshold
                if status["status"] == "ok":
                    status["status"] = "warning"
                status["message"] += f" | {days_used}/{doc.max_days} days used"
            else:
                status["message"] += f" | {days_used}/{doc.max_days} days used"

        results.append(status)

    return results
