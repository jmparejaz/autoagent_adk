"""
Modular Registry System for Nexus ADK Platform
Allows dynamic registration of databases, knowledge bases, and file processors.
"""
import logging
from typing import Any, Dict, List, Optional, Callable, Type
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConnection:
    """Database connection configuration."""
    name: str
    connection_string: str
    connection_type: str = "postgresql"  # postgresql, mysql, sqlite, etc.
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    # Connection pool settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30

    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class KnowledgeBase:
    """Knowledge base configuration."""
    name: str
    collection_name: str
    source_type: str  # chromadb, vertexai, pinecone, etc.
    description: str = ""

    # Indexing settings
    chunk_size: int = 1000
    chunk_overlap: int = 100
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Metadata
    tags: List[str] = field(default_factory=list)
    document_count: int = 0


@dataclass
class FileProcessor:
    """File processor configuration."""
    name: str
    file_extensions: List[str]
    processor_type: str  # pdf, image, document, data, custom

    # Processing settings
    extract_text: bool = True
    extract_images: bool = False
    ocr_enabled: bool = False

    # Custom processor function
    process_function: Optional[Callable] = None

    description: str = ""


class Registry:
    """Central registry for all modular components."""

    def __init__(self):
        self._databases: Dict[str, DatabaseConnection] = {}
        self._knowledge_bases: Dict[str, KnowledgeBase] = {}
        self._file_processors: Dict[str, FileProcessor] = {}

    # ==================== Database Management ====================

    def register_database(self, config: DatabaseConnection) -> None:
        """Register a database connection."""
        self._databases[config.name] = config
        logger.info(f"Registered database: {config.name} ({config.connection_type})")

    def get_database(self, name: str) -> Optional[DatabaseConnection]:
        """Get a database connection by name."""
        return self._databases.get(name)

    def list_databases(self) -> List[DatabaseConnection]:
        """List all registered databases."""
        return list(self._databases.values())

    def unregister_database(self, name: str) -> bool:
        """Unregister a database."""
        if name in self._databases:
            del self._databases[name]
            logger.info(f"Unregistered database: {name}")
            return True
        return False

    # ==================== Knowledge Base Management ====================

    def register_knowledge_base(self, config: KnowledgeBase) -> None:
        """Register a knowledge base."""
        self._knowledge_bases[config.name] = config
        logger.info(f"Registered knowledge base: {config.name} ({config.source_type})")

    def get_knowledge_base(self, name: str) -> Optional[KnowledgeBase]:
        """Get a knowledge base by name."""
        return self._knowledge_bases.get(name)

    def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """List all registered knowledge bases."""
        return list(self._knowledge_bases.values())

    def unregister_knowledge_base(self, name: str) -> bool:
        """Unregister a knowledge base."""
        if name in self._knowledge_bases:
            del self._knowledge_bases[name]
            logger.info(f"Unregistered knowledge base: {name}")
            return True
        return False

    # ==================== File Processor Management ====================

    def register_file_processor(self, config: FileProcessor) -> None:
        """Register a file processor."""
        self._file_processors[config.name] = config
        logger.info(f"Registered file processor: {config.name} ({config.processor_type})")

    def get_file_processor(self, name: str) -> Optional[FileProcessor]:
        """Get a file processor by name."""
        return self._file_processors.get(name)

    def get_processor_for_extension(self, extension: str) -> Optional[FileProcessor]:
        """Get the appropriate processor for a file extension."""
        extension = extension.lower().lstrip('.')
        for processor in self._file_processors.values():
            if extension in processor.file_extensions:
                return processor
        return None

    def list_file_processors(self) -> List[FileProcessor]:
        """List all registered file processors."""
        return list(self._file_processors.values())

    def unregister_file_processor(self, name: str) -> bool:
        """Unregister a file processor."""
        if name in self._file_processors:
            del self._file_processors[name]
            logger.info(f"Unregistered file processor: {name}")
            return True
        return False

    # ==================== Status ====================

    def get_status(self) -> Dict[str, Any]:
        """Get registry status."""
        return {
            "databases": {
                "count": len(self._databases),
                "names": list(self._databases.keys())
            },
            "knowledge_bases": {
                "count": len(self._knowledge_bases),
                "names": list(self._knowledge_bases.keys())
            },
            "file_processors": {
                "count": len(self._file_processors),
                "names": list(self._file_processors.keys())
            }
        }


# Global registry instance
registry = Registry()


# ==================== Convenience Functions ====================

def register_database(
    name: str,
    connection_string: str,
    connection_type: str = "postgresql",
    **kwargs
) -> DatabaseConnection:
    """Register a database connection."""
    config = DatabaseConnection(
        name=name,
        connection_string=connection_string,
        connection_type=connection_type,
        **kwargs
    )
    registry.register_database(config)
    return config


def register_knowledge_base(
    name: str,
    collection_name: str,
    source_type: str = "chromadb",
    **kwargs
) -> KnowledgeBase:
    """Register a knowledge base."""
    config = KnowledgeBase(
        name=name,
        collection_name=collection_name,
        source_type=source_type,
        **kwargs
    )
    registry.register_knowledge_base(config)
    return config


def register_file_processor(
    name: str,
    file_extensions: List[str],
    processor_type: str,
    **kwargs
) -> FileProcessor:
    """Register a file processor."""
    config = FileProcessor(
        name=name,
        file_extensions=file_extensions,
        processor_type=processor_type,
        **kwargs
    )
    registry.register_file_processor(config)
    return config
