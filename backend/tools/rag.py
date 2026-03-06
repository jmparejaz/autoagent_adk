"""
RAG (Retrieval-Augmented Generation) tools for Nexus ADK Platform.
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import chromadb
from chromadb.config import Settings
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import settings

logger = logging.getLogger(__name__)


class KnowledgeBaseTool:
    """Tool for RAG-based knowledge base queries."""

    def __init__(self):
        self.persist_dir = settings.chroma_persist_dir
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collections = {}

    def get_or_create_collection(self, name: str):
        """Get or create a collection."""
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"description": f"Knowledge base collection: {name}"}
            )
        return self.collections[name]

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Add documents to a collection.

        Args:
            collection_name: Name of the collection
            documents: List of document texts
            ids: Optional list of document IDs
            metadatas: Optional metadata for each document

        Returns:
            Success status
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]

            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )

            return {
                "success": True,
                "documents_added": len(documents),
                "collection_name": collection_name
            }

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return {"success": False, "error": str(e)}

    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query a collection.

        Args:
            collection_name: Name of the collection
            query_text: Query text
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Query results
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )

            formatted_results = {
                "success": True,
                "query": query_text,
                "results": []
            }

            if results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    result_item = {
                        "document": doc,
                        "id": results["ids"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None,
                        "metadata": results["metadatas"][0][i] if "metadatas" in results else None
                    }
                    formatted_results["results"].append(result_item)

            return formatted_results

        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {"success": False, "error": str(e)}

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            collection = self.client.get_collection(collection_name)
            return {
                "success": True,
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_collections(self) -> List[str]:
        """List all collections."""
        try:
            return self.client.list_collections()
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []

    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            return {"success": True, "deleted": collection_name}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global knowledge base tool instance
kb_tool = KnowledgeBaseTool()


def query_knowledge_base(
    collection_name: str,
    query: str,
    n_results: int = 5
) -> str:
    """
    ADK Tool: Query the knowledge base.

    Args:
        collection_name: Name of the knowledge base collection
        query: Query text
        n_results: Number of results to return

    Returns:
        JSON string with query results
    """
    result = kb_tool.query(collection_name, query, n_results)
    return json.dumps(result, default=str)


def add_to_knowledge_base(
    collection_name: str,
    documents: str,
    ids: Optional[str] = None,
    metadatas: Optional[str] = None
) -> str:
    """
    ADK Tool: Add documents to knowledge base.

    Args:
        collection_name: Name of the collection
        documents: JSON array of document texts
        ids: Optional JSON array of document IDs
        metadatas: Optional JSON array of metadata objects

    Returns:
        JSON string with success status
    """
    try:
        doc_list = json.loads(documents)
        id_list = json.loads(ids) if ids else None
        meta_list = json.loads(metadatas) if metadatas else None

        result = kb_tool.add_documents(
            collection_name,
            doc_list,
            id_list,
            meta_list
        )
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def search_knowledge_base(
    collection_name: str,
    query: str,
    n_results: int = 3
) -> str:
    """
    ADK Tool: Search the knowledge base with context retrieval.

    Args:
        collection_name: Name of the knowledge base
        query: Search query
        n_results: Number of results

    Returns:
        JSON string with formatted search results
    """
    result = kb_tool.query(collection_name, query, n_results)

    if result.get("success"):
        # Format for better readability
        formatted = {
            "query": query,
            "results": [],
            "context": ""
        }

        for item in result.get("results", []):
            formatted["results"].append({
                "content": item["document"],
                "source": item.get("metadata", {}).get("source", "Unknown"),
                "score": 1 - (item.get("distance", 0) or 0)
            })

        # Build context string
        context_parts = [r["content"] for r in formatted["results"]]
        formatted["context"] = "\n\n".join(context_parts)

        return json.dumps(formatted, indent=2)

    return json.dumps(result, default=str)


def get_kb_collections() -> str:
    """
    ADK Tool: List all knowledge base collections.

    Returns:
        JSON string with collection names
    """
    collections = kb_tool.list_collections()
    return json.dumps({"collections": [c.name for c in collections]})


def get_collection_info(collection_name: str) -> str:
    """
    ADK Tool: Get information about a collection.

    Args:
        collection_name: Name of the collection

    Returns:
        JSON string with collection info
    """
    info = kb_tool.get_collection_info(collection_name)
    return json.dumps(info, default=str)
