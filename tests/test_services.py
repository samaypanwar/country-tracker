import pytest
from datetime import date, timedelta
import pandas as pd
from country_tracker.models import TravelEntry, Document
from country_tracker.services import (
    expand_travel_dates,
    calculate_residency,
    check_compliance,
)


def test_expand_travel_dates_basic():
    entries = [
        TravelEntry(
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 3),
            country="Country A",
            iso3="CTA",
        ),
        TravelEntry(
            start_date=date(2023, 1, 5),
            end_date=date(2023, 1, 5),
            country="Country B",
            iso3="CTB",
        ),
    ]

    daily_df = expand_travel_dates(entries)

    # Expected dates: Jan 1, 2, 3, 5 (Jan 4 is missing)
    assert len(daily_df) == 4
    assert isinstance(daily_df.index, pd.DatetimeIndex)

    # Check content
    assert daily_df.loc["2023-01-01", "country"] == "Country A"
    assert daily_df.loc["2023-01-02", "country"] == "Country A"
    assert daily_df.loc["2023-01-03", "country"] == "Country A"
    assert daily_df.loc["2023-01-05", "country"] == "Country B"

    # Check missing date is not in index
    assert pd.Timestamp("2023-01-04") not in daily_df.index


def test_expand_travel_dates_overlap():
    # Test that later entry overwrites earlier one
    entries = [
        TravelEntry(
            start_date=date(2023, 1, 1), end_date=date(2023, 1, 5), country="Country A"
        ),
        TravelEntry(
            start_date=date(2023, 1, 4), end_date=date(2023, 1, 6), country="Country B"
        ),
    ]

    daily_df = expand_travel_dates(entries)

    # Jan 1, 2, 3 -> A
    # Jan 4, 5 -> B (overwrite)
    # Jan 6 -> B

    assert daily_df.loc["2023-01-03", "country"] == "Country A"
    assert daily_df.loc["2023-01-04", "country"] == "Country B"
    assert daily_df.loc["2023-01-05", "country"] == "Country B"
    assert daily_df.loc["2023-01-06", "country"] == "Country B"


def test_expand_travel_dates_missing_end_date():
    # Test that missing end_date (NaT) defaults to today
    entry = TravelEntry(
        start_date=date.today() - timedelta(days=5),
        end_date=pd.NaT,
        country="Country C",
        iso3="CTC",
    )

    daily_df = expand_travel_dates([entry])

    # Should cover start_date to today (inclusive) -> 6 days
    assert len(daily_df) == 6
    assert daily_df.index.max().date() == date.today()
    assert daily_df.iloc[-1]["country"] == "Country C"


def test_calculate_residency_rolling():
    # Create a daily DF manually for testing calculation
    dates = pd.date_range(start="2023-01-01", end="2023-12-31")
    data = []
    for d in dates:
        if d.month <= 6:  # First 6 months (~181 days) in Country A
            data.append({"country": "Country A", "iso3": "CTA"})
        else:
            data.append({"country": "Country B", "iso3": "CTB"})

    daily_df = pd.DataFrame(data, index=dates)

    # Check residency for Country A on July 1st (should be ~181 days in last 365)
    res_a = calculate_residency(
        daily_df, "Country A", window_days=365, reference_date=date(2023, 7, 1)
    )
    # Jan 1 to June 30 is ~181 days. July 1 is Country B.
    # So looking back 365 days from July 1 includes all of Jan-June.
    assert 180 <= res_a <= 182

    # Check residency for Country B on July 1st (should be 1 day: July 1st itself)
    # Wait, in my mock data July 1st is Country B.
    res_b = calculate_residency(
        daily_df, "Country B", window_days=365, reference_date=date(2023, 7, 1)
    )
    assert res_b == 1


def test_check_compliance_expiry():
    # Document expires in 10 days, renew_before is 30 days -> Should flag warning
    doc = Document(
        doc_type="visa",
        country="Country A",
        name="Visa A",
        issue_date=date(2023, 1, 1),
        expiry_date=date(2023, 12, 31),
        renew_before_days=30,
    )

    # Today is Dec 20, 2023 (11 days before expiry)
    today = date(2023, 12, 20)

    # We need to mock daily_df but it's not used for expiry check
    daily_df = pd.DataFrame()

    status = check_compliance([doc], daily_df, reference_date=today)

    assert len(status) == 1
    assert status[0]["status"] == "warning"
    assert "Expires in 11 days" in status[0]["message"]


def test_check_compliance_90_180():
    # Document has 90/180 rule
    doc = Document(
        doc_type="visa",
        country="Schengen",
        name="Tourist Visa",
        issue_date=date(2023, 1, 1),
        expiry_date=date(2024, 1, 1),
        max_days=90,
        window_days=180,
    )

    # User has stayed 85 days in last 180 days
    # Create daily_df
    dates = pd.date_range(start="2023-01-01", end="2023-06-30")
    data = []
    # 85 days in Schengen
    for i, d in enumerate(dates):
        if i < 85:
            data.append({"country": "Schengen"})
        else:
            data.append({"country": "Other"})

    daily_df = pd.DataFrame(data, index=dates)

    # Check on June 30th
    today = date(2023, 6, 30)

    status = check_compliance([doc], daily_df, reference_date=today)

    assert len(status) == 1
    # 85 days in data, but window is 180 days ending June 30.
    # Jan 1 to June 30 is 181 days. So Jan 1 is excluded from the window.
    # Thus only 84 days are counted.
    assert status[0]["days_used"] == 84
    assert status[0]["days_remaining"] == 6
    # 84 is >= 80 (90-10), so it should be a warning
    assert status[0]["status"] == "warning"

    # Now test violation (91 days)
    data = []
    for i, d in enumerate(dates):
        # Shift days to ensure they fall in the window (start from index 1 which is Jan 2)
        if 1 <= i < 92:  # 91 days starting Jan 2
            data.append({"country": "Schengen"})
        else:
            data.append({"country": "Other"})
    daily_df = pd.DataFrame(data, index=dates)

    status = check_compliance([doc], daily_df, reference_date=today)
    assert status[0]["days_used"] == 91
    assert status[0]["status"] == "violation"
