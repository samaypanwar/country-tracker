import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_world_map(
    data_df: pd.DataFrame, projection: str = "natural earth", color_scale: str = "Blues"
) -> go.Figure:
    """
    Creates a styled choropleth map using Plotly.

    Args:
        data_df: DataFrame with columns 'iso3', 'country', 'days'
        projection: Projection type (e.g., 'natural earth', 'orthographic')
        color_scale: Color scale name (e.g., 'Blues', 'Plasma')

    Returns:
        plotly.graph_objects.Figure
    """
    if data_df.empty:
        return go.Figure()

    # Get color scale object if it's a string name from px.colors.sequential
    # But px.choropleth handles string names directly too.
    # We'll just pass the string.

    fig = px.choropleth(
        data_df,
        locations="iso3",
        color="days",
        hover_name="country",
        color_continuous_scale=color_scale,
        projection=projection,
    )

    # Apply clean styling
    fig.update_geos(
        showcountries=True,
        countrycolor="Black",
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="azure",
        showlakes=True,
        lakecolor="azure",
        projection_type=projection,
    )

    # Remove margins for a cleaner look
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo=dict(
            bgcolor="rgba(0,0,0,0)"  # Transparent background
        ),
    )

    return fig
