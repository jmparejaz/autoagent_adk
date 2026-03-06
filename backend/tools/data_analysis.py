"""
Data analysis and visualization tools for Nexus ADK Platform.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.tools import db_tool

logger = logging.getLogger(__name__)


class DataAnalysisTool:
    """Tool for data analysis and visualization."""

    def __init__(self):
        self.allowed_operations = ["SELECT", "INSERT", "UPDATE", "DELETE"]

    def analyze_data(
        self,
        data: Union[List[Dict], pd.DataFrame],
        analysis_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Perform data analysis.

        Args:
            data: Input data (list of dicts or DataFrame)
            analysis_type: Type of analysis to perform

        Returns:
            Analysis results
        """
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        if analysis_type == "summary":
            return self.get_summary_stats(df)
        elif analysis_type == "correlation":
            return self.get_correlation_matrix(df)
        elif analysis_type == "distribution":
            return self.get_distribution(df)
        elif analysis_type == "outliers":
            return self.detect_outliers(df)
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}

    def get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for DataFrame."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        result = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_counts": df.isnull().sum().to_dict(),
            "numeric_summary": {},
            "categorical_summary": {}
        }

        if len(numeric_cols) > 0:
            result["numeric_summary"] = df[numeric_cols].describe().to_dict()

        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            for col in cat_cols:
                result["categorical_summary"][col] = {
                    "unique_count": int(df[col].nunique()),
                    "top_values": {k: int(v) for k, v in df[col].value_counts().head(5).to_dict().items()}
                }

        return result

    def get_correlation_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get correlation matrix for numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            return {"error": "No numeric columns found"}

        corr = numeric_df.corr()
        return {
            "correlation_matrix": corr.to_dict(),
            "strong_correlations": self._find_strong_correlations(corr)
        }

    def _find_strong_correlations(self, corr: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
        """Find strong correlations between variables."""
        strong = []
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                val = corr.iloc[i, j]
                if abs(val) >= threshold:
                    strong.append({
                        "var1": corr.columns[i],
                        "var2": corr.columns[j],
                        "correlation": round(val, 3)
                    })
        return strong

    def get_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get distribution information for all columns."""
        result = {}

        for col in df.columns:
            if df[col].dtype in [np.number]:
                result[col] = {
                    "type": "numeric",
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "q25": float(df[col].quantile(0.25)),
                    "q75": float(df[col].quantile(0.75))
                }
            else:
                result[col] = {
                    "type": "categorical",
                    "unique_count": int(df[col].nunique()),
                    "top_values": {k: int(v) for k, v in df[col].value_counts().head(10).to_dict().items()}
                }

        return result

    def detect_outliers(self, df: pd.DataFrame, method: str = "iqr") -> Dict[str, Any]:
        """Detect outliers in numeric columns."""
        result = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if method == "iqr":
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                outliers = df[(df[col] < lower) | (df[col] > upper)][col]
            else:  # z-score
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = df[z_scores > 3][col]

            result[col] = {
                "outlier_count": int(len(outliers)),
                "outlier_percentage": round(len(outliers) / len(df) * 100, 2),
                "outlier_values": outliers.tolist()[:10]
            }

        return result

    def create_chart(
        self,
        data: Union[List[Dict], pd.DataFrame],
        chart_type: str,
        x: Optional[str] = None,
        y: Optional[str] = None,
        title: str = "Chart",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Plotly chart.

        Args:
            data: Input data
            chart_type: Type of chart (bar, line, scatter, pie, histogram, box)
            x: X-axis column
            y: Y-axis column
            title: Chart title
            **kwargs: Additional chart parameters

        Returns:
            Chart configuration as JSON
        """
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        try:
            fig = None

            if chart_type == "bar":
                if x and y:
                    fig = px.bar(df, x=x, y=y, title=title, **kwargs)
                elif x:
                    fig = px.bar(df, x=x, title=title, **kwargs)

            elif chart_type == "line":
                if x and y:
                    fig = px.line(df, x=x, y=y, title=title, **kwargs)

            elif chart_type == "scatter":
                if x and y:
                    fig = px.scatter(df, x=x, y=y, title=title, **kwargs)
                elif x:
                    fig = px.scatter(df, x=x, title=title, **kwargs)

            elif chart_type == "pie":
                if x and y:
                    fig = px.pie(df, names=x, values=y, title=title, **kwargs)
                elif x:
                    fig = px.pie(df, names=x, title=title, **kwargs)

            elif chart_type == "histogram":
                if x:
                    fig = px.histogram(df, x=x, title=title, **kwargs)
                else:
                    fig = px.histogram(df, title=title, **kwargs)

            elif chart_type == "box":
                if x and y:
                    fig = px.box(df, x=x, y=y, title=title, **kwargs)
                elif x:
                    fig = px.box(df, x=x, title=title, **kwargs)

            elif chart_type == "heatmap":
                numeric_df = df.select_dtypes(include=[np.number])
                if not numeric_df.empty:
                    corr = numeric_df.corr()
                    fig = px.imshow(corr, title=title, **kwargs)

            if fig is None:
                return {"error": f"Could not create {chart_type} chart"}

            # Apply professional styling
            fig.update_layout(
                template="plotly_white",
                font=dict(family="Inter, sans-serif", size=12),
                title_font=dict(size=16, family="Inter, sans-serif"),
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=40, r=40, t=60, b=40)
            )

            return {
                "success": True,
                "chart_type": chart_type,
                "title": title,
                "json_config": json.loads(fig.to_json()),
                "html": fig.to_html(fullscreen=False, include_plotlyjs='cdn')
            }

        except Exception as e:
            logger.error(f"Chart creation error: {e}")
            return {"error": str(e)}


# Global data analysis tool instance
analysis_tool = DataAnalysisTool()


def analyze_data_from_query(query: str, analysis_type: str = "summary") -> str:
    """
    ADK Tool: Execute SQL query and analyze the results.

    Args:
        query: SQL SELECT query
        analysis_type: Type of analysis to perform

    Returns:
        JSON string with analysis results
    """
    result = db_tool.execute_query(query)
    if not result.get("success"):
        return json.dumps(result)

    analysis = analysis_tool.analyze_data(result["data"], analysis_type)
    return json.dumps(analysis, default=str)


def create_visualization(
    query: str,
    chart_type: str,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: str = "Data Visualization"
) -> str:
    """
    ADK Tool: Create a chart from SQL query results.

    Args:
        query: SQL SELECT query
        chart_type: Type of chart (bar, line, scatter, pie, histogram, box, heatmap)
        x: X-axis column name
        y: Y-axis column name
        title: Chart title

    Returns:
        JSON string with chart configuration
    """
    result = db_tool.execute_query(query)
    if not result.get("success"):
        return json.dumps(result)

    chart = analysis_tool.create_chart(
        result["data"],
        chart_type,
        x=x,
        y=y,
        title=title
    )
    return json.dumps(chart, default=str)


def create_interactive_chart(
    data: str,
    chart_type: str,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: str = "Interactive Chart"
) -> str:
    """
    ADK Tool: Create an interactive chart from JSON data.

    Args:
        data: JSON string or list of data
        chart_type: Type of chart to create
        x: X-axis column
        y: Y-axis column
        title: Chart title

    Returns:
        JSON string with chart configuration
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)

        chart = analysis_tool.create_chart(
            data,
            chart_type,
            x=x,
            y=y,
            title=title
        )
        return json.dumps(chart, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})
