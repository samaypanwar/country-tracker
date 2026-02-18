import pandas as pd
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from country_tracker.models import TravelEntry, Document


class DataLoader:
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)

    def load_travel_log(self) -> List[TravelEntry]:
        file_path = self.data_dir / "travel_log.csv"
        if not file_path.exists():
            return []

        try:
            df = pd.read_csv(file_path)
            # Basic validation could go here
            if df.empty:
                return []

            entries = []
            for _, row in df.iterrows():
                # Handle potential NaN values for optional fields
                iso3 = row["iso3"] if pd.notna(row.get("iso3")) else None
                notes = row["notes"] if pd.notna(row.get("notes")) else None

                entry = TravelEntry(
                    start_date=pd.to_datetime(row["start_date"]).date(),
                    end_date=pd.to_datetime(row["end_date"]).date(),
                    country=row["country"],
                    iso3=iso3,
                    notes=notes,
                )
                entries.append(entry)
            return entries
        except Exception as e:
            # For now, just return empty list on error or maybe log it
            print(f"Error loading travel log: {e}")
            return []

    def load_documents(self) -> List[Document]:
        file_path = self.data_dir / "documents.csv"
        if not file_path.exists():
            return []

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return []

            docs = []
            for _, row in df.iterrows():
                # Handle optional fields
                max_days = (
                    int(row["max_days"]) if pd.notna(row.get("max_days")) else None
                )
                window_days = (
                    int(row["window_days"])
                    if pd.notna(row.get("window_days"))
                    else None
                )
                renew_before = (
                    int(row["renew_before_days"])
                    if pd.notna(row.get("renew_before_days"))
                    else None
                )
                notes = row["notes"] if pd.notna(row.get("notes")) else None

                doc = Document(
                    doc_type=row["doc_type"],
                    country=row["country"],
                    name=row["name"],
                    issue_date=pd.to_datetime(row["issue_date"]).date(),
                    expiry_date=pd.to_datetime(row["expiry_date"]).date(),
                    max_days=max_days,
                    window_days=window_days,
                    renew_before_days=renew_before,
                    notes=notes,
                )
                docs.append(doc)
            return docs
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []

    def append_travel_entry(self, entry: TravelEntry):
        file_path = self.data_dir / "travel_log.csv"

        new_row = {
            "start_date": entry.start_date,
            "end_date": entry.end_date,
            "country": entry.country,
            "iso3": entry.iso3,
            "notes": entry.notes,
        }

        df = pd.DataFrame([new_row])

        if file_path.exists():
            df.to_csv(file_path, mode="a", header=False, index=False)
        else:
            df.to_csv(file_path, mode="w", header=True, index=False)

    def append_document(self, doc: Document):
        file_path = self.data_dir / "documents.csv"

        new_row = {
            "doc_type": doc.doc_type,
            "country": doc.country,
            "name": doc.name,
            "issue_date": doc.issue_date,
            "expiry_date": doc.expiry_date,
            "max_days": doc.max_days,
            "window_days": doc.window_days,
            "renew_before_days": doc.renew_before_days,
            "notes": doc.notes,
        }

        df = pd.DataFrame([new_row])

        if file_path.exists():
            df.to_csv(file_path, mode="a", header=False, index=False)
        else:
            df.to_csv(file_path, mode="w", header=True, index=False)
