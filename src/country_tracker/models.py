from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class TravelEntry:
    start_date: date
    end_date: date
    country: str
    iso3: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class Document:
    doc_type: str  # 'passport' or 'visa'
    country: str
    name: str
    issue_date: date
    expiry_date: date
    max_days: Optional[int] = None
    window_days: Optional[int] = None
    renew_before_days: Optional[int] = None
    notes: Optional[str] = None

@dataclass
class ResidencyStatus:
    country: str
    days_last_183: int
    days_last_365: int
    days_custom: int
    current_streak: int
