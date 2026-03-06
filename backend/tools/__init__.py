"""
Database tools for Nexus ADK Platform.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from backend.config import settings

logger = logging.getLogger(__name__)


class DatabaseTool:
    """Tool for executing PostgreSQL queries."""

    def __init__(self):
        self.config = settings.database
        self._connection = None

    def _get_connection(self):
        """Get or create database connection."""
        try:
            if self._connection is None or self._connection.closed:
                self._connection = psycopg2.connect(
                    self.config.psycopg2_string,
                    cursor_factory=RealDictCursor
                )
            return self._connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters (optional)
            fetch: Whether to fetch results (for SELECT queries)

        Returns:
            Dictionary with query results or error information
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)

                if fetch:
                    results = cursor.fetchall()
                    # Convert to list of dicts
                    data = [dict(row) for row in results]

                    # Get column names
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []

                    return {
                        "success": True,
                        "data": data,
                        "columns": columns,
                        "row_count": len(data)
                    }
                else:
                    connection.commit()
                    return {
                        "success": True,
                        "affected_rows": cursor.rowcount
                    }

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def get_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        result = self.execute_query(query)
        if result.get("success"):
            return [row["table_name"] for row in result["data"]]
        return []

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table."""
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """
        result = self.execute_query(query, params=(table_name,))
        return result

    def get_sample_data(
        self,
        table_name: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get sample data from a table."""
        query = sql.SQL("SELECT * FROM {} LIMIT {}").format(
            sql.Identifier(table_name),
            sql.Literal(limit)
        )
        return self.execute_query(str(query))

    def get_column_values(
        self,
        table_name: str,
        column: str,
        limit: int = 100
    ) -> List[Any]:
        """Get unique values from a column."""
        query = sql.SQL("SELECT DISTINCT {} FROM {} LIMIT {}").format(
            sql.Identifier(column),
            sql.Identifier(table_name),
            sql.Literal(limit)
        )
        result = self.execute_query(str(query))
        if result.get("success"):
            return [row[column] for row in result["data"]]
        return []

    def get_location_data(
        self,
        table_name: str,
        lat_column: str,
        lon_column: str,
        condition: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Get location data for mapping."""
        query = f"SELECT *, {lat_column} as lat, {lon_column} as lon FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        query += f" LIMIT {limit}"

        return self.execute_query(query)

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


# Global database tool instance
db_tool = DatabaseTool()


def execute_sql(query: str) -> Dict[str, Any]:
    """
    ADK Tool: Execute SQL query on PostgreSQL database.

    Args:
        query: SQL SELECT query to execute

    Returns:
        Query
    """
    result = db_tool.execute_query(query)
    return json.dumps(result, default=str)


def list_tables() -> str:
    """
    ADK Tool: List all available tables in the database.

    Returns:
        JSON string of table names
    """
    tables = db_tool.get_tables()
    return json.dumps({"tables": tables})


def describe_table(table_name: str) -> str:
    """
    ADK Tool: Get schema information for a table.

    Args:
        table_name: Name of the table

    Returns:
        JSON string of table schema
    """
    schema = db_tool.get_table_schema(table_name)
    return json.dumps(schema, default=str)


def get_sample_data(table_name: str, limit: int = 10) -> str:
    """
    ADK Tool: Get sample data from a table.

    Args:
        table_name: Name of the table
        limit: Number of rows to fetch

    Returns:
        JSON string of sample data
    """
    data = db_tool.get_sample_data(table_name, limit)
    return json.dumps(data, default=str)


def get_locations_for_map(
    table_name: str,
    lat_column: str,
    lon_column: str,
    condition: Optional[str] = None,
    limit: int = 1000
) -> str:
    """
    ADK Tool: Get location data for creating maps.

    Args:
        table_name: Name of the table with location data
        lat_column: Name of the latitude column
        lon_column: Name of the longitude column
        condition: Optional WHERE clause
        limit: Maximum number of rows

    Returns:
        JSON string of location data
    """
    data = db_tool.get_location_data(table_name, lat_column, lon_column, condition, limit)
    return json.dumps(data, default=str)
