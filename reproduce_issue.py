from country_tracker.data import DataLoader
import pandas as pd


def test_reproduce_travel_log_error():
    loader = DataLoader()
    print(f"Loading from {loader.data_dir}")

    try:
        entries = loader.load_travel_log()
        print(f"Loaded {len(entries)} entries")
        if entries:
            last_entry = entries[-1]
            print(f"Last entry: {last_entry}")
            print(f"Last entry end_date type: {type(last_entry.end_date)}")
    except Exception as e:
        print(f"Caught error: {e}")


if __name__ == "__main__":
    test_reproduce_travel_log_error()
