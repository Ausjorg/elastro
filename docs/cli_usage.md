# Elastro CLI Usage Guide

The Elastro package provides a powerful command-line interface (CLI) for managing Elasticsearch indices, documents, and datastreams. This guide explains how to use the CLI effectively.

## Installation

The CLI is automatically installed when you install the elastic-module package:

```bash
pip install elastic-module
```

## Configuration

Before using the CLI, you'll need to configure your Elasticsearch connection details.

### Initialize Configuration

```bash
elastic-module config init
```

This creates a default configuration file at `~/.elastic/config.yaml`. You can use the `--profile` option to create a named profile:

```bash
elastic-module config init --profile production
```

### Set Configuration Values

You can set configuration values using the `config set` command:

```bash
elastic-module config set elasticsearch.hosts '["http://localhost:9200"]'
elastic-module config set elasticsearch.auth.username my_username
elastic-module config set elasticsearch.auth.password my_password
```

### List Configuration

To view your current configuration:

```bash
elastic-module config list
```

### Get Configuration Value

To get a specific configuration value:

```bash
elastic-module config get elasticsearch.hosts
```

## Global Options

The following options can be used with any command:

- `--config, -c`: Path to configuration file
- `--profile, -p`: Configuration profile to use (default: "default")
- `--host, -h`: Elasticsearch host(s) (can be specified multiple times)
- `--output, -o`: Output format (json, yaml, table)
- `--verbose, -v`: Enable verbose output
- `--version`: Show version and exit
- `--help`: Show help message and exit

## Index Management

The CLI provides commands for managing Elasticsearch indices.

### Create Index

```bash
elastic-module index create INDEX_NAME [OPTIONS]
```

Options:
- `--shards`: Number of shards (default: 1)
- `--replicas`: Number of replicas (default: 1)
- `--mapping`: Path to mapping file (JSON format)
- `--settings`: Path to settings file (JSON format)

### Get Index

```bash
elastic-module index get INDEX_NAME
```

### Check if Index Exists

```bash
elastic-module index exists INDEX_NAME
```

### Update Index

```bash
elastic-module index update INDEX_NAME --settings SETTINGS_FILE
```

### Delete Index

```bash
elastic-module index delete INDEX_NAME [--force]
```

The `--force` option skips the confirmation prompt.

### Open Index

```bash
elastic-module index open INDEX_NAME
```

### Close Index

```bash
elastic-module index close INDEX_NAME
```

## Document Management

The CLI provides commands for managing documents within indices.

### Index a Document

```bash
elastic-module doc index INDEX_NAME [OPTIONS]
```

Options:
- `--id`: Document ID (optional)
- `--file`: Path to document file (JSON format)

If no file is provided, the document is read from stdin.

### Bulk Index Documents

```bash
elastic-module doc bulk INDEX_NAME --file DOCUMENTS_FILE
```

The file should contain a JSON array of documents.

### Get Document

```bash
elastic-module doc get INDEX_NAME DOCUMENT_ID
```

### Search Documents

```bash
elastic-module doc search INDEX_NAME [QUERY] [OPTIONS]
```

Options:
- `--size`: Maximum number of results (default: 10)
- `--from`: Starting offset (default: 0)
- `--file`: Path to query file (JSON format)

If no query is provided, a match_all query is used.

### Update Document

```bash
elastic-module doc update INDEX_NAME DOCUMENT_ID --file DOCUMENT_FILE [--partial]
```

The `--partial` flag enables partial document updates.

### Delete Document

```bash
elastic-module doc delete INDEX_NAME DOCUMENT_ID
```

### Bulk Delete Documents

```bash
elastic-module doc bulk-delete INDEX_NAME --file IDS_FILE
```

The file should contain a JSON array of document IDs.

## Datastream Management

The CLI provides commands for managing Elasticsearch datastreams.

### Create Datastream

```bash
elastic-module datastream create DATASTREAM_NAME [--index-pattern INDEX_PATTERN]
```

### List Datastreams

```bash
elastic-module datastream list [--pattern PATTERN]
```

### Get Datastream

```bash
elastic-module datastream get DATASTREAM_NAME
```

### Delete Datastream

```bash
elastic-module datastream delete DATASTREAM_NAME
```

### Rollover Datastream

```bash
elastic-module datastream rollover DATASTREAM_NAME [--conditions CONDITIONS_FILE]
```

## Utility Commands

The CLI provides utility commands for common Elasticsearch operations.

### Cluster Health

```bash
elastic-module utils health [--level LEVEL]
```

The level can be one of: cluster, indices, shards.

### Index Templates

```bash
elastic-module utils templates list [--pattern PATTERN]
elastic-module utils templates get TEMPLATE_NAME
```

### Aliases

```bash
elastic-module utils aliases list [--index INDEX]
```

## Examples

### Create an Index with Custom Mapping

```bash
elastic-module index create my_index --shards 3 --replicas 2 --mapping mapping.json
```

### Index a Document

```bash
echo '{"title": "Test", "content": "This is a test document"}' | elastic-module doc index my_index
```

### Search Documents

```bash
elastic-module doc search my_index "title:Test" --size 20
```

### Using Multiple Profiles

```bash
# Initialize production profile
elastic-module config init --profile production

# Set production configuration
elastic-module config set elasticsearch.hosts '["https://prod-es:9200"]' --profile production

# Use production profile for operations
elastic-module --profile production index list
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to Elasticsearch, verify your configuration:

```bash
elastic-module config list
```

Ensure that the hosts, username, and password are correct.

### Permission Errors

Permission errors often occur when your user doesn't have the required permissions in Elasticsearch. Check your user's roles and permissions in Elasticsearch.

### Data Format Errors

When indexing or updating documents, ensure that your JSON is valid. You can validate your JSON with:

```bash
cat document.json | jq
```

## Additional Resources

For more advanced usage and API documentation, refer to the project's [API documentation](./api_docs.md).
