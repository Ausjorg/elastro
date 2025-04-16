"""
Index management module.

This module provides functionality for managing Elasticsearch indices.
"""

from typing import Dict, Optional, Any, List, Union
from elastro.core.client import ElasticsearchClient
from elastro.core.errors import IndexError, ValidationError
from elastro.core.validation import Validator


class IndexManager:
    """
    Manager for Elasticsearch index operations.

    This class provides methods for creating, updating, and managing Elasticsearch indices.
    """

    def __init__(self, client: ElasticsearchClient):
        """
        Initialize the index manager.

        Args:
            client: ElasticsearchClient instance
        """
        self.client = client
        self._client = client  # Add this for compatibility with tests
        self.validator = Validator()

    def create(
        self,
        name: str,
        settings: Optional[Dict[str, Any]] = None,
        mappings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Elasticsearch index.

        Args:
            name: Name of the index
            settings: Index settings
            mappings: Index mappings

        Returns:
            Dict containing creation response

        Raises:
            ValidationError: If input validation fails
            IndexError: If index creation fails
        """
        if not name:
            raise ValidationError("Index name is required")

        # Prepare request body
        body: Dict[str, Any] = {}

        # Handle case where settings contains both settings and mappings
        if settings and "mappings" in settings and mappings is None:
            mappings = settings.get("mappings")
            if "settings" in settings:
                settings = settings.get("settings")

        # Process settings
        if settings:
            try:
                self.validator.validate_index_settings(settings)
                body["settings"] = settings
            except ValidationError as e:
                raise ValidationError(f"Invalid index settings: {str(e)}")

        # Process mappings
        if mappings:
            try:
                self.validator.validate_index_mappings(mappings)
                body["mappings"] = mappings
            except ValidationError as e:
                raise ValidationError(f"Invalid index mappings: {str(e)}")

        try:
            response = self.client.client.indices.create(index=name, body=body)
            return response
        except Exception as e:
            raise IndexError(f"Failed to create index '{name}': {str(e)}")

    def exists(self, name: str) -> bool:
        """
        Check if an index exists.

        Args:
            name: Name of the index

        Returns:
            True if index exists, False otherwise

        Raises:
            IndexError: If the check operation fails
        """
        if not name:
            raise ValidationError("Index name is required")

        try:
            return self.client.client.indices.exists(index=name)
        except Exception as e:
            raise IndexError(f"Failed to check if index '{name}' exists: {str(e)}")

    def get(self, name: str) -> Dict[str, Any]:
        """
        Get index information.

        Args:
            name: Name of the index

        Returns:
            Dict containing index information

        Raises:
            IndexError: If index doesn't exist or operation fails
        """
        if not name:
            raise ValidationError("Index name is required")

        try:
            if not self.exists(name):
                raise IndexError(f"Index '{name}' does not exist")

            response = self.client.client.indices.get(index=name)
            return response
        except IndexError:
            raise
        except Exception as e:
            raise IndexError(f"Failed to get index '{name}': {str(e)}")

    def update(self, name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update index settings.

        Args:
            name: Name of the index
            settings: Updated index settings

        Returns:
            Dict containing update response

        Raises:
            ValidationError: If input validation fails
            IndexError: If index update fails
        """
        if not name:
            raise ValidationError("Index name is required")

        if not settings:
            raise ValidationError("Settings are required for update")

        try:
            self.validator.validate_index_settings(settings)
        except ValidationError as e:
            raise ValidationError(f"Invalid index settings: {str(e)}")

        try:
            if not self.exists(name):
                raise IndexError(f"Index '{name}' does not exist")

            # Unlike create, update expects the settings without the 'settings' wrapper
            response = self.client.client.indices.put_settings(
                index=name,
                body=settings
            )
            return response
        except IndexError:
            raise
        except Exception as e:
            raise IndexError(f"Failed to update index '{name}': {str(e)}")

    def delete(self, name: str) -> Dict[str, Any]:
        """
        Delete an index.

        Args:
            name: Name of the index

        Returns:
            Dict containing deletion response

        Raises:
            IndexError: If index deletion fails
        """
        if not name:
            raise ValidationError("Index name is required")

        try:
            if not self.exists(name):
                raise IndexError(f"Index '{name}' does not exist")

            response = self.client.client.indices.delete(index=name)
            return response
        except IndexError:
            raise
        except Exception as e:
            raise IndexError(f"Failed to delete index '{name}': {str(e)}")

    def open(self, name: str) -> Dict[str, Any]:
        """
        Open an index.

        Args:
            name: Name of the index

        Returns:
            Dict containing open response

        Raises:
            IndexError: If index open operation fails
        """
        if not name:
            raise ValidationError("Index name is required")

        try:
            if not self.exists(name):
                raise IndexError(f"Index '{name}' does not exist")

            response = self.client.client.indices.open(index=name)
            return response
        except IndexError:
            raise
        except Exception as e:
            raise IndexError(f"Failed to open index '{name}': {str(e)}")

    def close(self, name: str) -> Dict[str, Any]:
        """
        Close an index.

        Args:
            name: Name of the index

        Returns:
            Dict containing close response

        Raises:
            IndexError: If index close operation fails
        """
        if not name:
            raise ValidationError("Index name is required")

        try:
            if not self.exists(name):
                raise IndexError(f"Index '{name}' does not exist")

            response = self.client.client.indices.close(index=name)
            return response
        except IndexError:
            raise
        except Exception as e:
            raise IndexError(f"Failed to close index '{name}': {str(e)}")
