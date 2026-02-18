import pytest
import pandas as pd
import plotly.graph_objects as go
from country_tracker.visualization import create_world_map


def test_create_world_map_structure():
    # Mock data
    data = {
        "iso3": ["USA", "FRA", "JPN"],
        "country": ["United States", "France", "Japan"],
        "days": [100, 50, 20],
    }
    df = pd.DataFrame(data)

    # Create map
    fig = create_world_map(df, projection="natural earth", color_scale="Blues")

    # Assertions
    assert isinstance(fig, go.Figure)

    # Check layout
    assert fig.layout.geo.projection.type == "natural earth"
    assert fig.layout.geo.showland is True
    assert fig.layout.geo.showocean is True

    # Check data
    assert len(fig.data) == 1
    assert fig.data[0].type == "choropleth"
    assert list(fig.data[0].locations) == ["USA", "FRA", "JPN"]


def test_create_world_map_orthographic():
    data = {"iso3": ["USA"], "country": ["USA"], "days": [10]}
    df = pd.DataFrame(data)

    fig = create_world_map(df, projection="orthographic")
    assert fig.layout.geo.projection.type == "orthographic"


def test_create_world_map_empty():
    df = pd.DataFrame(columns=["iso3", "country", "days"])
    fig = create_world_map(df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
