import pytest
from datetime import date
import pandas as pd
from country_tracker.models import TravelEntry, Document
from country_tracker.data import DataLoader
import os

@pytest.fixture
def sample_data_dir(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    
    travel_csv = d / "travel_log.csv"
    travel_csv.write_text("start_date,end_date,country,iso3,notes\n2023-01-01,2023-01-15,United States,USA,Holiday")
    
    docs_csv = d / "documents.csv"
    docs_csv.write_text("doc_type,country,name,issue_date,expiry_date,max_days,window_days,renew_before_days,notes\nvisa,Schengen,Tourist Visa,2023-01-01,2024-01-01,90,180,30,Multi-entry")
    
    return d

def test_load_travel_log(sample_data_dir):
    loader = DataLoader(data_dir=sample_data_dir)
    travel_log = loader.load_travel_log()
    
    assert len(travel_log) == 1
    entry = travel_log[0]
    assert isinstance(entry, TravelEntry)
    assert entry.start_date == date(2023, 1, 1)
    assert entry.end_date == date(2023, 1, 15)
    assert entry.country == "United States"
    assert entry.iso3 == "USA"
    assert entry.notes == "Holiday"

def test_load_documents(sample_data_dir):
    loader = DataLoader(data_dir=sample_data_dir)
    documents = loader.load_documents()
    
    assert len(documents) == 1
    doc = documents[0]
    assert isinstance(doc, Document)
    assert doc.doc_type == "visa"
    assert doc.country == "Schengen"
    assert doc.name == "Tourist Visa"
    assert doc.issue_date == date(2023, 1, 1)
    assert doc.expiry_date == date(2024, 1, 1)
    assert doc.max_days == 90
    assert doc.window_days == 180
    assert doc.renew_before_days == 30
    assert doc.notes == "Multi-entry"

def test_load_missing_files(tmp_path):
    loader = DataLoader(data_dir=tmp_path)
    # Should return empty lists or handle gracefully
    assert loader.load_travel_log() == []
    assert loader.load_documents() == []
