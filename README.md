# Residency + Visa Tracker

A Streamlit application to track travel history, calculate residency days (rolling windows), and monitor visa/document expiration and compliance rules.

## Features

- **Overview**: Current location and top countries by residency.
- **Residency**: Detailed rolling window analysis (183/365 days) and yearly breakdown.
- **World Map**: Interactive heatmap of days spent per country.
  - Supports multiple projections (Natural Earth, Orthographic/Globe).
  - Customizable color scales (Blues, Plasma, Viridis, etc.).
  - Filter by specific years or view all-time history.
- **Documents**: Visa expiry tracking and 90/180 rule compliance checks.
- **Data Entry**: Forms to easily add travel logs and documents.

## Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run the application:
   ```bash
   poetry run streamlit run src/country_tracker/app.py
   ```

## Data

Data is stored in CSV files in the `data/` directory:
- `data/travel_log.csv`: Tracks travel history (start/end dates, country).
- `data/documents.csv`: Tracks document details (visas, passports, expiry rules).

## Testing

Run tests with:
```bash
poetry run pytest
```
