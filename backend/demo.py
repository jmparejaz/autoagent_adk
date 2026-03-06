"""
Demo Mode for Nexus ADK Platform
=================================

This module provides demo functionality that works without a database.
Use this for testing and demonstration purposes.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DemoDatabase:
    """
    Demo database that simulates PostgreSQL responses.
    Use this when no real database is available.
    """

    def __init__(self):
        # Sample data for demos
        self._tables = {
            "customers": self._generate_customers(),
            "orders": self._generate_orders(),
            "products": self._generate_products(),
            "locations": self._generate_locations(),
            "sales": self._generate_sales()
        }

    def _generate_customers(self) -> List[Dict]:
        """Generate sample customer data."""
        np.random.seed(42)
        n = 100
        return [
            {
                "customer_id": i + 1,
                "name": f"Customer {i+1}",
                "email": f"customer{i+1}@example.com",
                "city": np.random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], n)[i],
                "state": np.random.choice(["NY", "CA", "IL", "TX", "AZ"], n)[i],
                "signup_date": f"2023-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
                "total_spent": round(np.random.uniform(100, 10000), 2)
            }
            for i in range(n)
        ]

    def _generate_orders(self) -> List[Dict]:
        """Generate sample order data."""
        np.random.seed(43)
        n = 200
        return [
            {
                "order_id": i + 1,
                "customer_id": np.random.randint(1, 101, n)[i],
                "product_id": np.random.randint(1, 21, n)[i],
                "quantity": np.random.randint(1, 10, n)[i],
                "order_date": f"2024-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
                "total": round(np.random.uniform(20, 500), 2),
                "status": np.random.choice(["pending", "shipped", "delivered", "cancelled"], n, p=[0.1, 0.3, 0.5, 0.1])[i]
            }
            for i in range(n)
        ]

    def _generate_products(self) -> List[Dict]:
        """Generate sample product data."""
        categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
        return [
            {"product_id": i+1, "name": f"Product {i+1}", "category": categories[i % 5],
             "price": round(10 + i * 5.5, 2), "stock": np.random.randint(0, 1000)}
            for i in range(20)
        ]

    def _generate_locations(self) -> List[Dict]:
        """Generate sample location data with coordinates."""
        # Major US cities with coordinates
        cities = [
            {"city": "New York", "lat": 40.7128, "lon": -74.0060, "population": 8336817},
            {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "population": 3979576},
            {"city": "Chicago", "lat": 41.8781, "lon": -87.6298, "population": 2693976},
            {"city": "Houston", "lat": 29.7604, "lon": -95.3698, "population": 2320268},
            {"city": "Phoenix", "lat": 33.4484, "lon": -112.0740, "population": 1680992},
            {"city": "Philadelphia", "lat": 39.9526, "lon": -75.1652, "population": 1584064},
            {"city": "San Antonio", "lat": 29.4241, "lon": -98.4936, "population": 1547253},
            {"city": "San Diego", "lat": 32.7157, "lon": -117.1611, "population": 1423851},
            {"city": "Dallas", "lat": 32.7767, "lon": -96.7970, "population": 1343573},
            {"city": "San Jose", "lat": 37.3382, "lon": -121.8863, "population": 1021795},
            {"city": "Austin", "lat": 30.2672, "lon": -97.7431, "population": 978908},
            {"city": "Jacksonville", "lat": 30.3322, "lon": -81.6557, "population": 911507},
            {"city": "San Francisco", "lat": 37.7749, "lon": -122.4194, "population": 881549},
            {"city": "Columbus", "lat": 39.9612, "lon": -82.9988, "population": 898553},
            {"city": "Indianapolis", "lat": 39.7684, "lon": -86.1581, "population": 867125},
        ]
        return [dict(city=c["city"], lat=c["lat"], lon=c["lon"], population=c["population"],
                    store_count=np.random.randint(1, 20)) for c in cities]

    def _generate_sales(self) -> List[Dict]:
        """Generate sample sales data."""
        np.random.seed(45)
        n = 150
        return [
            {
                "sale_id": i + 1,
                "date": f"2024-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
                "region": np.random.choice(["North", "South", "East", "West"], n)[i],
                "product_category": np.random.choice(["Electronics", "Clothing", "Home", "Sports", "Books"], n)[i],
                "revenue": round(np.random.uniform(1000, 50000), 2),
                "units_sold": np.random.randint(10, 500, n)[i]
            }
            for i in range(n)
        ]

    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a demo query.
        Simple implementation - parses table name from query.
        """
        query_lower = query.lower().strip()

        # Extract table name
        table_name = None
        for tbl in self._tables.keys():
            if tbl in query_lower:
                table_name = tbl
                break

        if not table_name:
            return {
                "success": False,
                "error": "No valid table found in query. Available tables: customers, orders, products, locations, sales"
            }

        # Simple query parsing
        df = pd.DataFrame(self._tables[table_name])

        # Handle WHERE clause (simple implementation)
        if "where" in query_lower:
            # Very simple parsing - just handle simple equality
            parts = query_lower.split("where")[1].strip()
            if "=" in parts:
                col, val = parts.split("=")[0].strip(), parts.split("=")[1].strip().strip("'\"")
                if col in df.columns:
                    try:
                        df = df[df[col] == val]
                    except:
                        pass

        # Handle ORDER BY
        if "order by" in query_lower:
            parts = query_lower.split("order by")[1].strip().split()[0]
            if parts in df.columns:
                ascending = "desc" not in query_lower
                df = df.sort_values(parts, ascending=ascending)

        # Handle LIMIT
        limit = 100
        if "limit" in query_lower:
            try:
                limit = int(query_lower.split("limit")[1].strip().split()[0])
            except:
                pass
        df = df.head(limit)

        return {
            "success": True,
            "data": df.to_dict(orient="records"),
            "columns": list(df.columns),
            "row_count": len(df)
        }

    def get_tables(self) -> List[str]:
        """Get list of available tables."""
        return list(self._tables.keys())

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table schema."""
        if table_name not in self._tables:
            return {"success": False, "error": "Table not found"}

        df = pd.DataFrame(self._tables[table_name])
        columns = []

        for col in df.columns:
            dtype = str(df[col].dtype)
            columns.append({
                "column_name": col,
                "data_type": dtype,
                "is_nullable": "YES",
                "character_maximum_length": None
            })

        return {
            "success": True,
            "data": columns,
            "columns": ["column_name", "data_type", "is_nullable", "character_maximum_length"]
        }


# Global demo database
demo_db = DemoDatabase()


def get_demo_data(table_name: str, limit: int = 10) -> Dict[str, Any]:
    """Get sample data from a demo table."""
    return demo_db.execute_query(f"SELECT * FROM {table_name} LIMIT {limit}")


def get_all_tables() -> List[str]:
    """Get all available demo tables."""
    return demo_db.get_tables()


def execute_demo_query(query: str) -> Dict[str, Any]:
    """Execute a demo query."""
    return demo_db.execute_query(query)
