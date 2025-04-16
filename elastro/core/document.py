"""
Document management module.

This module provides functionality for managing Elasticsearch documents.
"""

from typing import Dict, List, Any, Optional, Union
from elastro.core.client import ElasticsearchClient
from elastro.core.errors import DocumentError, ValidationError, OperationError
from elastro.core.validation import Validator


class DocumentManager:
    """
    Manager for Elasticsearch document operations.

    This class provides methods for indexing, updating, and searching documents.
    """

    def __init__(self, client: ElasticsearchClient):
        """
        Initialize the document manager.

        Args:
            client: ElasticsearchClient instance
        """
        self.client = client
        self._client = client  # Add this for compatibility with tests
        self.validator = Validator()

    def index(
        self,
        index: str,
        id: Optional[str],
        document: Dict[str, Any],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Index a document.

        Args:
            index: Name of the index
            id: Document ID (optional)
            document: Document data
            refresh: Whether to refresh the index immediately

        Returns:
            Dict containing indexing response

        Raises:
            ValidationError: If input validation fails
            DocumentError: If document indexing fails
        """
        # Validate inputs
        if not index:
            raise ValidationError("Index name cannot be empty")

        # Document validation could be expanded based on schema
        if not document or not isinstance(document, dict):
            raise ValidationError("Document must be a non-empty dictionary")

        try:
            # Prepare indexing parameters
            params = {
                "index": index,
                "document": document,
                "refresh": "true" if refresh else "false"
            }

            # Add ID if provided
            if id:
                params["id"] = id

            # Execute the index operation
            return self.client.client.index(**params)
        except Exception as e:
            raise DocumentError(f"Failed to index document: {str(e)}")

    def bulk_index(
        self,
        index: str,
        documents: List[Dict[str, Any]],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Bulk index multiple documents.

        Args:
            index: Name of the index
            documents: List of documents to index
            refresh: Whether to refresh the index immediately

        Returns:
            Dict containing bulk indexing response

        Raises:
            ValidationError: If input validation fails
            OperationError: If bulk indexing fails
        """
        # Validate inputs
        if not index:
            raise ValidationError("Index name cannot be empty")

        if not documents or not isinstance(documents, list):
            raise ValidationError("Documents must be a non-empty list")

        try:
            # Prepare the bulk operation
            operations = []
            for doc in documents:
                # Add index operation
                index_op = {"index": {"_index": index}}
                # If document has an ID field, use it
                if "_id" in doc:
                    index_op["index"]["_id"] = doc["_id"]
                    # Remove _id from the actual document
                    doc_copy = doc.copy()
                    doc_copy.pop("_id", None)
                    operations.append(index_op)
                    operations.append(doc_copy)
                else:
                    operations.append(index_op)
                    operations.append(doc)

            # Execute the bulk operation
            return self.client.client.bulk(
                operations=operations,
                refresh="true" if refresh else "false"
            )
        except Exception as e:
            raise OperationError(f"Failed to bulk index documents: {str(e)}")

    def get(self, index: str, id: str) -> Dict[str, Any]:
        """
        Get a document by ID.

        Args:
            index: Name of the index
            id: Document ID

        Returns:
            Dict containing document data

        Raises:
            DocumentError: If document doesn't exist or get operation fails
        """
        # Validate inputs
        if not index:
            raise ValidationError("Index name cannot be empty")

        if not id:
            raise ValidationError("Document ID cannot be empty")

        try:
            response = self.client.client.get(index=index, id=id)
            return response
        except Exception as e:
            raise DocumentError(f"Failed to get document: {str(e)}")

    def update(
        self,
        index: str,
        id: str,
        document: Dict[str, Any],
        partial: bool = True,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Update a document.

        Args:
            index: Name of the index
            id: Document ID
            document: Updated document data or partial document
            partial: Whether this is a partial update
            refresh: Whether to refresh the index immediately

        Returns:
            Dict containing update response

        Raises:
            ValidationError: If input validation fails
            DocumentError: If document update fails
        """
        # Validate inputs
        if not index:
            raise ValidationError("Index name cannot be empty")

        if not id:
            raise ValidationError("Document ID cannot be empty")

        if not document or not isinstance(document, dict):
            raise ValidationError("Document must be a non-empty dictionary")

        try:
            if partial:
                # For partial updates, wrap in "doc" field
                body = {"doc": document}
                return self.client.client.update(
                    index=index,
                    id=id,
                    body=body,
                    refresh="true" if refresh else "false"
                )
            else:
                # For full document updates, just index it again
                return self.index(index=index, id=id, document=document, refresh=refresh)
        except Exception as e:
            raise DocumentError(f"Failed to update document: {str(e)}")

    def delete(
        self,
        index: str,
        id: str,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a document by ID.

        Args:
            index: Name of the index
            id: Document ID
            refresh: Whether to refresh the index immediately

        Returns:
            Dict containing deletion response

        Raises:
            ValidationError: If input validation fails
            DocumentError: If document deletion fails
        """
        # Validate inputs
        if not index:
            raise ValidationError("Index name cannot be empty")

        if not id:
            raise ValidationError("Document ID cannot be empty")

        try:
            return self.client.client.delete(
                index=index,
                id=id,
                refresh="true" if refresh else "false"
            )
        except Exception as e:
            raise DocumentError(f"Failed to delete document: {str(e)}")

    def bulk_delete(
        self,
        index: str,
        ids: List[str],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Bulk delete multiple documents by ID.

        Args:
            index: Name of the index
            ids: List of document IDs to delete
            refresh: Whether to refresh the index immediately

        Returns:
            Dict containing bulk deletion response

        Raises:
            ValidationError: If input validation fails
            OperationError: If bulk deletion fails
        """
        # Validate inputs
        if not index:
            raise ValidationError("Index name cannot be empty")

        if not ids or not isinstance(ids, list):
            raise ValidationError("IDs must be a non-empty list")

        try:
            # Prepare the bulk operation
            operations = []
            for doc_id in ids:
                operations.append({"delete": {"_index": index, "_id": doc_id}})

            # Execute the bulk operation
            return self.client.client.bulk(
                operations=operations,
                refresh="true" if refresh else "false"
            )
        except Exception as e:
            raise OperationError(f"Failed to bulk delete documents: {str(e)}")

    def search(
        self,
        index: str,
        query: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for documents.

        Args:
            index: Name of the index
            query: Elasticsearch query DSL
            options: Additional search options like size, from, sort, etc.

        Returns:
            Dict containing search results

        Raises:
            ValidationError: If input validation fails
            DocumentError: If search fails
        """
        # Validate inputs
        if not index:
            raise ValidationError("Index name cannot be empty")

        if not query:
            raise ValidationError("Query cannot be empty")

        # Prepare search body
        body = {"query": query}

        # Add search options if provided
        if options:
            for key, value in options.items():
                if key in ["size", "from", "sort", "track_total_hits"]:
                    body[key] = value
                elif key in ["_source", "aggs", "aggregations", "highlight"]:
                    body[key] = value

        search_params = {"index": index, "body": body}

        try:
            return self.client.client.search(**search_params)
        except Exception as e:
            raise DocumentError(f"Failed to search documents: {str(e)}")
