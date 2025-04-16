"""Index template management utilities for Elasticsearch."""
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field, ConfigDict

from elastro.core.client import ElasticsearchClient
from elastro.core.errors import OperationError


class TemplateDefinition(BaseModel):
    """Pydantic model for index template validation."""
    name: str
    index_patterns: List[str]
    template: Dict[str, Any] = Field(default_factory=dict)
    version: Optional[int] = None
    priority: Optional[int] = None
    composed_of: List[str] = Field(default_factory=list)
    meta: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class TemplateManager:
    """Manager for Elasticsearch index templates operations.

    This class provides methods to create, get, update, and delete index templates.
    """

    def __init__(self, client: ElasticsearchClient):
        """Initialize the TemplateManager.

        Args:
            client: The Elasticsearch client instance.
        """
        self._client = client
        self._es = client.client

    def create(self, template_def: Union[Dict[str, Any], TemplateDefinition]) -> bool:
        """Create a new index template.

        Args:
template_def: Template definition as a dict or TemplateDefinition instance.

        Returns:
            bool: True if template was created successfully.

        Raises:
            OperationError: If template creation fails.
        """
        try:
            if isinstance(template_def, dict):
                template_def = TemplateDefinition(**template_def)

            response = self._es.indices.put_index_template(
                name=template_def.name,
                body={
                    "index_patterns": template_def.index_patterns,
                    "template": template_def.template,
                    "version": template_def.version,
                    "priority": template_def.priority,
                    "composed_of": template_def.composed_of,
                    "_meta": template_def.meta
                }
            )
            return response.get("acknowledged", False)
        except Exception as e:
            raise OperationError(f"Failed to create template {template_def.name}: {str(e)}")

    def get(self, name: str) -> Dict[str, Any]:
        """Get an index template by name.

        Args:
            name: Name of the template to retrieve.

        Returns:
            dict: Template configuration.

        Raises:
            OperationError: If template retrieval fails.
        """
        try:
            response = self._es.indices.get_index_template(name=name)
            if "index_templates" in response and len(response["index_templates"]) > 0:
                return response["index_templates"][0]
            return {}
        except Exception as e:
            raise OperationError(f"Failed to get template {name}: {str(e)}")

    def exists(self, name: str) -> bool:
        """Check if an index template exists.

        Args:
            name: Name of the template to check.

        Returns:
            bool: True if template exists, False otherwise.
        """
        try:
            return self._es.indices.exists_index_template(name=name)
        except Exception:
            return False

    def delete(self, name: str) -> bool:
        """Delete an index template.

        Args:
            name: Name of the template to delete.

        Returns:
            bool: True if template was deleted successfully.

        Raises:
            OperationError: If template deletion fails.
        """
        try:
            response = self._es.indices.delete_index_template(name=name)
            return response.get("acknowledged", False)
        except Exception as e:
            raise OperationError(f"Failed to delete template {name}: {str(e)}")

    def list(self) -> List[str]:
        """List all index templates.

        Returns:
            list: List of template names.

        Raises:
            OperationError: If listing templates fails.
        """
        try:
            response = self._es.indices.get_index_template()
            return [t["name"] for t in response.get("index_templates", [])]
        except Exception as e:
            raise OperationError(f"Failed to list templates: {str(e)}")
