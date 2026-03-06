"""
Map generation tools for Nexus ADK Platform.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
import folium
from folium.plugins import MarkerCluster, Fullscreen
from branca.element import Element
import pandas as pd

from backend.tools import db_tool
from backend.config import settings

logger = logging.getLogger(__name__)


class MapGenerationTool:
    """Tool for generating interactive maps."""

    def __init__(self):
        self.maps_api_key = settings.google.maps_api_key

    def create_map_from_data(
        self,
        data: Union[List[Dict], pd.DataFrame],
        lat_column: str = "lat",
        lon_column: str = "lon",
        popup_fields: Optional[List[str]] = None,
        tooltip_fields: Optional[List[str]] = None,
        map_type: str = "openstreetmap",
        center: Optional[List[float]] = None,
        zoom: int = 10
    ) -> Dict[str, Any]:
        """
        Create an interactive map from location data.

        Args:
            data: List of dictionaries with location data
            lat_column: Name of latitude column
            lon_column: Name of longitude column
            popup_fields: Fields to show in popup
            tooltip_fields: Fields to show in tooltip
            map_type: Type of map (openstreetmap, cartodbpositron, stamenwatercolor)
            center: [lat, lon] to center the map
            zoom: Initial zoom level

        Returns:
            Map configuration and HTML
        """
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        # Check for valid coordinates
        if lat_column not in df.columns or lon_column not in df.columns:
            return {
                "success": False,
                "error": f"Columns {lat_column} and {lon_column} must be present in data"
            }

        # Filter valid coordinates
        df = df.dropna(subset=[lat_column, lon_column])
        if len(df) == 0:
            return {
                "success": False,
                "error": "No valid location data found"
            }

        # Calculate center if not provided
        if center is None:
            center = [df[lat_column].mean(), df[lon_column].mean()]

        # Create base map
        if map_type == "cartodbpositron":
            tiles = "cartodbpositron"
        elif map_type == "stamenwatercolor":
            tiles = "Stamen Watercolor"
        else:
            tiles = "OpenStreetMap"

        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=tiles
        )

        # Add fullscreen control
        Fullscreen().add_to(m)

        # Determine popup and tooltip fields
        if popup_fields is None:
            popup_fields = [col for col in df.columns if col not in [lat_column, lon_column]]
        if tooltip_fields is None:
            tooltip_fields = popup_fields[:3]

        # Add markers
        for idx, row in df.iterrows():
            lat = row[lat_column]
            lon = row[lon_column]

            # Create popup content
            popup_html = "<div style='font-family: Inter, sans-serif; min-width: 200px;'>"
            for field in popup_fields:
                if field in row and pd.notna(row[field]):
                    popup_html += f"<p><strong>{field}:</strong> {row[field]}</p>"
            popup_html += "</div>"

            # Create tooltip content
            tooltip = " | ".join([str(row[f]) for f in tooltip_fields if f in row])

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=tooltip
            ).add_to(m)

        # Add marker clustering for large datasets
        if len(df) > 100:
            marker_cluster = MarkerCluster().add_to(m)
            for idx, row in df.iterrows():
                lat = row[lat_column]
                lon = row[lon_column]
                tooltip = " | ".join([str(row[f]) for f in tooltip_fields if f in row])

                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=tooltip
                ).add_to(marker_cluster)

        # Add title
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; z-index: 1000;
             background-color: white; padding: 10px 20px; border-radius: 5px;
             box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-family: Inter, sans-serif;">
            <h4 style="margin: 0; color: #333;">Interactive Map ({len(df)} locations)</h4>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        return {
            "success": True,
            "location_count": len(df),
            "center": center,
            "zoom": zoom,
            "map_type": map_type,
            "html": m._repr_html_(),
            "bounds": [[df[lat_column].min(), df[lon_column].min()],
                       [df[lat_column].max(), df[lon_column].max()]]
        }

    def create_heatmap(
        self,
        data: Union[List[Dict], pd.DataFrame],
        lat_column: str = "lat",
        lon_column: str = "lon",
        intensity_column: Optional[str] = None,
        radius: int = 25,
        blur: int = 15
    ) -> Dict[str, Any]:
        """Create a heatmap from location data."""
        from folium.plugins import HeatMap

        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        if lat_column not in df.columns or lon_column not in df.columns:
            return {"success": False, "error": "Location columns not found"}

        df = df.dropna(subset=[lat_column, lon_column])

        # Prepare heat data
        heat_data = []
        for idx, row in df.iterrows():
            lat = row[lat_column]
            lon = row[lon_column]
            if intensity_column and intensity_column in row:
                weight = float(row[intensity_column])
            else:
                weight = 1
            heat_data.append([lat, lon, weight])

        # Create map
        center = [df[lat_column].mean(), df[lon_column].mean()]
        m = folium.Map(location=center, zoom_start=10, tiles="cartodbpositron")

        # Add heatmap
        HeatMap(
            heat_data,
            radius=radius,
            blur=blur,
            max_zoom=13
        ).add_to(m)

        return {
            "success": True,
            "location_count": len(df),
            "html": m._repr_html_()
        }

    def create_cluster_map(
        self,
        data: Union[List[Dict], pd.DataFrame],
        lat_column: str = "lat",
        lon_column: str = "lon",
        popup_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a clustered marker map."""
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        if lat_column not in df.columns or lon_column not in df.columns:
            return {"success": False, "error": "Location columns not found"}

        df = df.dropna(subset=[lat_column, lon_column])

        center = [df[lat_column].mean(), df[lon_column].mean()]
        m = folium.Map(location=center, zoom_start=10)

        if popup_fields is None:
            popup_fields = [col for col in df.columns if col not in [lat_column, lon_column]]

        # Add marker cluster
        marker_cluster = MarkerCluster().add_to(m)

        for idx, row in df.iterrows():
            popup_html = "<div style='font-family: Inter, sans-serif;'>"
            for field in popup_fields:
                if field in row and pd.notna(row[field]):
                    popup_html += f"<p><strong>{field}:</strong> {row[field]}</p>"
            popup_html += "</div>"

            folium.Marker(
                location=[row[lat_column], row[lon_column]],
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(marker_cluster)

        return {
            "success": True,
            "location_count": len(df),
            "html": m._repr_html_()
        }


# Global map generation tool instance
map_tool = MapGenerationTool()


def generate_map(
    query: str,
    lat_column: str,
    lon_column: str,
    popup_fields: Optional[str] = None,
    map_type: str = "openstreetmap",
    title: str = "Interactive Map"
) -> str:
    """
    ADK Tool: Generate an interactive map from database query.

    Args:
        query: SQL SELECT query with location data
        lat_column: Name of latitude column
        lon_column: Name of longitude column
        popup_fields: Comma-separated list of fields for popup
        map_type: Type of map (openstreetmap, cartodbpositron, stamenwatercolor)
        title: Map title

    Returns:
        JSON string with map HTML
    """
    result = db_tool.execute_query(query)
    if not result.get("success"):
        return json.dumps(result)

    popup_list = popup_fields.split(",") if popup_fields else None

    map_result = map_tool.create_map_from_data(
        result["data"],
        lat_column=lat_column,
        lon_column=lon_column,
        popup_fields=popup_list,
        map_type=map_type
    )

    return json.dumps(map_result, default=str)


def create_map_from_json(
    data: str,
    lat_column: str = "lat",
    lon_column: str = "lon",
    popup_fields: Optional[str] = None,
    map_type: str = "openstreetmap"
) -> str:
    """
    ADK Tool: Create an interactive map from JSON data.

    Args:
        data: JSON string with location data
        lat_column: Name of latitude column
        lon_column: Name of longitude column
        popup_fields: Comma-separated list of fields for popup
        map_type: Type of map

    Returns:
        JSON string with map HTML
    """
    try:
        data_list = json.loads(data)
        if isinstance(data_list, dict):
            data_list = [data_list]

        popup_list = popup_fields.split(",") if popup_fields else None

        map_result = map_tool.create_map_from_data(
            data_list,
            lat_column=lat_column,
            lon_column=lon_column,
            popup_fields=popup_list,
            map_type=map_type
        )

        return json.dumps(map_result, default=str)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def create_heatmap_from_query(
    query: str,
    lat_column: str = "lat",
    lon_column: str = "lon",
    intensity_column: Optional[str] = None
) -> str:
    """
    ADK Tool: Create a heatmap from database query.

    Args:
        query: SQL SELECT query with location data
        lat_column: Name of latitude column
        lon_column: Name of longitude column
        intensity_column: Column for heat intensity

    Returns:
        JSON string with heatmap HTML
    """
    result = db_tool.execute_query(query)
    if not result.get("success"):
        return json.dumps(result)

    heatmap = map_tool.create_heatmap(
        result["data"],
        lat_column=lat_column,
        lon_column=lon_column,
        intensity_column=intensity_column
    )

    return json.dumps(heatmap, default=str)
