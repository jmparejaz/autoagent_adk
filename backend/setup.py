"""
Nexus ADK Platform - Setup Module
==================================

Use this module to register your custom:
- Database connections
- Knowledge bases
- File processors

Example Usage:
--------------

# Add a new database connection
from backend.setup import setup

setup.register_database(
    name="sales_db",
    connection_string="postgresql://user:pass@localhost:5432/sales",
    description="Sales database",
    tags=["sales", "analytics"]
)

# Add a new knowledge base
setup.register_knowledge_base(
    name="company_policies",
    collection_name="hr_policies",
    description="Company HR policies and procedures",
    chunk_size=1500
)

# Add a custom file processor
setup.register_file_processor(
    name="excel_processor",
    file_extensions=["xlsx", "xls"],
    processor_type="data",
    description="Excel file processor"
)

# Initialize everything
setup.initialize()
"""

import logging
from typing import Any, Dict, List, Optional

from backend.tools.registry import (
    registry,
    DatabaseConnection,
    KnowledgeBase,
    FileProcessor,
    register_database,
    register_knowledge_base,
    register_file_processor
)
from backend.tools import db_tool
from backend.tools.rag import kb_tool

logger = logging.getLogger(__name__)


class Setup:
    """Setup class for registering custom components."""

    def __init__(self):
        self._initialized = False

    def register_database(
        self,
        name: str,
        connection_string: str,
        connection_type: str = "postgresql",
        description: str = "",
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> DatabaseConnection:
        """Register a database connection."""
        return register_database(
            name=name,
            connection_string=connection_string,
            connection_type=connection_type,
            description=description,
            tags=tags or [],
            **kwargs
        )

    def register_knowledge_base(
        self,
        name: str,
        collection_name: str,
        source_type: str = "chromadb",
        description: str = "",
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> KnowledgeBase:
        """Register a knowledge base."""
        return register_knowledge_base(
            name=name,
            collection_name=collection_name,
            source_type=source_type,
            description=description,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_model=embedding_model,
            tags=tags or [],
            **kwargs
        )

    def register_file_processor(
        self,
        name: str,
        file_extensions: List[str],
        processor_type: str,
        description: str = "",
        extract_text: bool = True,
        extract_images: bool = False,
        ocr_enabled: bool = False,
        process_function: Optional[callable] = None,
        **kwargs
    ) -> FileProcessor:
        """Register a file processor."""
        return register_file_processor(
            name=name,
            file_extensions=file_extensions,
            processor_type=processor_type,
            description=description,
            extract_text=extract_text,
            extract_images=extract_images,
            ocr_enabled=ocr_enabled,
            process_function=process_function,
            **kwargs
        )

    def initialize(self) -> None:
        """
        Initialize all registered components.

        This will:
        - Test database connections
        - Initialize knowledge base indexes
        - Register file processors with the system
        """
        if self._initialized:
            logger.warning("Setup already initialized")
            return

        logger.info("Initializing Nexus ADK Platform components...")

        # Initialize databases
        for db in registry.list_databases():
            logger.info(f"Initializing database: {db.name}")

        # Initialize knowledge bases
        for kb in registry.list_knowledge_bases():
            logger.info(f"Initializing knowledge base: {kb.name}")
            # Create collection if it doesn't exist
            try:
                kb_tool.get_or_create_collection(kb.collection_name)
            except Exception as e:
                logger.error(f"Failed to initialize knowledge base {kb.name}: {e}")

        # Initialize file processors
        for fp in registry.list_file_processors():
            logger.info(f"Registered file processor: {fp.name}")

        self._initialized = True
        logger.info("Nexus ADK Platform initialization complete")

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "initialized": self._initialized,
            "registry": registry.get_status()
        }


# Default setup with common configurations
def setup_default() -> Setup:
    """
    Create a Setup instance with default configurations.

    This sets up:
    - Default PostgreSQL connection (from settings)
    - Default knowledge base collection
    - Default file processors for common file types
    """
    setup = Setup()

    # Register default PostgreSQL from settings
    from backend.config import settings
    if settings.database.password:  # Only if password is configured
        setup.register_database(
            name="default_postgres",
            connection_string=settings.database.connection_string,
            connection_type="postgresql",
            description="Default PostgreSQL database",
            tags=["default", "primary"]
        )

    # Register default knowledge base
    setup.register_knowledge_base(
        name="default_docs",
        collection_name="company_documents",
        description="Default company documents knowledge base",
        tags=["default", "documents"]
    )

    # Register default file processors
    # PDF
    setup.register_file_processor(
        name="pdf_processor",
        file_extensions=["pdf"],
        processor_type="pdf",
        description="PDF document processor"
    )

    # Images
    setup.register_file_processor(
        name="image_processor",
        file_extensions=["jpg", "jpeg", "png", "gif", "webp", "bmp"],
        processor_type="image",
        description="Image file processor",
        extract_images=True
    )

    # Documents
    setup.register_file_processor(
        name="document_processor",
        file_extensions=["docx", "doc", "txt", "md"],
        processor_type="document",
        description="Text document processor"
    )

    # Data files
    setup.register_file_processor(
        name="data_processor",
        file_extensions=["csv", "xlsx", "xls", "json"],
        processor_type="data",
        description="Data file processor"
    )

    return setup


# Global setup instance
setup = setup_default()
