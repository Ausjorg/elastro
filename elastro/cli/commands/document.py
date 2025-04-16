"""
Document management commands for the CLI.
"""

import click
import json
import sys
from elastro.core.client import ElasticsearchClient
from elastro.core.document import DocumentManager
from elastro.core.errors import OperationError

@click.command("index")
@click.argument("index", type=str)
@click.option("--id", type=str, help="Document ID")
@click.option("--file", type=click.Path(exists=True, readable=True), help="Path to document file")
@click.pass_obj
def index_document(client, index, id, file):
    """Index a document."""
    document_manager = DocumentManager(client)

    # Load document data
    if file:
        with open(file, 'r') as f:
            document = json.load(f)
    else:
        # Read from stdin if no file provided
        document = json.loads(sys.stdin.read())

    try:
        result = document_manager.index(index, id, document)
        click.echo(json.dumps(result, indent=2))
        click.echo(f"Document indexed successfully in '{index}'.")
    except OperationError as e:
        click.echo(f"Error indexing document: {str(e)}", err=True)
        exit(1)

@click.command("bulk")
@click.argument("index", type=str)
@click.option("--file", type=click.Path(exists=True, readable=True), required=True, help="Path to bulk documents file")
@click.pass_obj
def bulk_index(client, index, file):
    """Bulk index documents."""
    document_manager = DocumentManager(client)

    # Load documents data
    with open(file, 'r') as f:
        documents = json.load(f)

    if not isinstance(documents, list):
        click.echo("Error: Bulk file must contain a JSON array of documents", err=True)
        exit(1)

    try:
        result = document_manager.bulk_index(index, documents)
        click.echo(json.dumps(result, indent=2))
        click.echo(f"Bulk indexing completed: {len(documents)} documents processed.")
    except OperationError as e:
        click.echo(f"Error in bulk indexing: {str(e)}", err=True)
        exit(1)

@click.command("get")
@click.argument("index", type=str)
@click.argument("id", type=str)
@click.pass_obj
def get_document(client, index, id):
    """Get a document by ID."""
    document_manager = DocumentManager(client)

    try:
        result = document_manager.get(index, id)
        click.echo(json.dumps(result, indent=2))
    except OperationError as e:
        click.echo(f"Error retrieving document: {str(e)}", err=True)
        exit(1)

@click.command("search")
@click.argument("index", type=str)
@click.argument("query", type=str, required=False)
@click.option("--size", type=int, default=10, help="Maximum number of results")
@click.option("--from", "from_", type=int, default=0, help="Starting offset")
@click.option("--file", type=click.Path(exists=True, readable=True), help="Path to query file")
@click.pass_obj
def search_documents(client, index, query, size, from_, file):
    """Search for documents."""
    document_manager = DocumentManager(client)

    # Determine query source
    if file:
        with open(file, 'r') as f:
            query_body = json.load(f)
    elif query:
        # Simple query string query
        query_body = {
            "query": {
                "query_string": {
                    "query": query
                }
            }
        }
    else:
        # Match all if no query provided
        query_body = {
            "query": {
                "match_all": {}
            }
        }

    # Add pagination
    options = {
        "size": size,
        "from": from_
    }

    try:
        results = document_manager.search(index, query_body, options)
        click.echo(json.dumps(results, indent=2))
    except OperationError as e:
        click.echo(f"Error searching documents: {str(e)}", err=True)
        exit(1)

@click.command("update")
@click.argument("index", type=str)
@click.argument("id", type=str)
@click.option("--file", type=click.Path(exists=True, readable=True), required=True, help="Path to document file")
@click.option("--partial", is_flag=True, help="Perform partial update")
@click.pass_obj
def update_document(client, index, id, file, partial):
    """Update a document."""
    document_manager = DocumentManager(client)

    # Load document data
    with open(file, 'r') as f:
        document = json.load(f)

    try:
        result = document_manager.update(index, id, document, partial)
        click.echo(json.dumps(result, indent=2))
        click.echo(f"Document '{id}' in index '{index}' updated successfully.")
    except OperationError as e:
        click.echo(f"Error updating document: {str(e)}", err=True)
        exit(1)

@click.command("delete")
@click.argument("index", type=str)
@click.argument("id", type=str)
@click.pass_obj
def delete_document(client, index, id):
    """Delete a document."""
    document_manager = DocumentManager(client)

    try:
        result = document_manager.delete(index, id)
        click.echo(json.dumps(result, indent=2))
        click.echo(f"Document '{id}' deleted from index '{index}'.")
    except OperationError as e:
        click.echo(f"Error deleting document: {str(e)}", err=True)
        exit(1)

@click.command("bulk-delete")
@click.argument("index", type=str)
@click.option("--file", type=click.Path(exists=True, readable=True), required=True, help="Path to IDs file")
@click.pass_obj
def bulk_delete(client, index, file):
    """Bulk delete documents."""
    document_manager = DocumentManager(client)

    # Load document IDs
    with open(file, 'r') as f:
        ids = json.load(f)

    if not isinstance(ids, list):
        click.echo("Error: IDs file must contain a JSON array of document IDs", err=True)
        exit(1)

    try:
        result = document_manager.bulk_delete(index, ids)
        click.echo(json.dumps(result, indent=2))
        click.echo(f"Bulk deletion completed: {len(ids)} documents processed.")
    except OperationError as e:
        click.echo(f"Error in bulk deletion: {str(e)}", err=True)
        exit(1)
