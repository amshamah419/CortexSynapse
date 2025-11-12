# Usage Examples

This document provides practical examples of using the Cortex MCP server.

## Installation and Setup

```bash
# Clone the repository
git clone https://github.com/amshamah419/Cortex-MCP.git
cd Cortex-MCP

# Install dependencies
pip install -e ".[dev]"

# Generate tools from OpenAPI specs
python -m codegen.generator

# Run the server
python -m server.main
```

## Generated Tools Overview

### XSIAM Tools

The XSIAM API provides security incident and alert management:

```python
# Available tools:
- list_incidents(limit: int | None, status: str | None)
- create_incident(name: str, severity: str, description: str | None)
- get_incident(incident_id: str)
- update_incident(incident_id: str, status: str | None, notes: str | None)
- list_alerts(severity: str | None, time_range: int | None)
```

### XSOAR Tools

The XSOAR API provides security orchestration and automation:

```python
# Available tools:
- list_playbooks(category: str | None)
- execute_playbook(playbook_id: str, inputs: Dict[str, Any] | None)
- list_investigations(status: str | None, limit: int | None)
- create_investigation(name: str, type: str, severity: int | None)
- search_indicators(query: str | None, type: str | None)
```

## Code Generation Examples

### Example 1: Simple GET Endpoint

**OpenAPI Spec:**
```yaml
paths:
  /users:
    get:
      operationId: listUsers
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
```

**Generated Code:**
```python
@server.call_tool()
async def list_users(
    limit: int | None = None,
) -> List[types.TextContent]:
    """..."""
    # Implementation auto-generated
```

### Example 2: POST with Request Body

**OpenAPI Spec:**
```yaml
paths:
  /incidents:
    post:
      operationId: createIncident
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - severity
              properties:
                name:
                  type: string
                severity:
                  type: string
```

**Generated Code:**
```python
@server.call_tool()
async def create_incident(
    name: str,
    severity: str,
) -> List[types.TextContent]:
    """..."""
    # Implementation handles required parameters
```

### Example 3: Path Parameters

**OpenAPI Spec:**
```yaml
paths:
  /incidents/{incident_id}:
    get:
      operationId: getIncident
      parameters:
        - name: incident_id
          in: path
          required: true
          schema:
            type: string
```

**Generated Code:**
```python
@server.call_tool()
async def get_incident(
    incident_id: str,
) -> List[types.TextContent]:
    """..."""
    # Path parameter automatically handled
```

## Docker Usage

### Build the Image

```bash
docker build -t cortex-mcp .
```

### Run the Container

```bash
docker run -i cortex-mcp
```

### Push to Registry

```bash
docker tag cortex-mcp ghcr.io/your-username/cortex-mcp:latest
docker push ghcr.io/your-username/cortex-mcp:latest
```

## Development Workflow

### Adding a New API

1. **Create OpenAPI Spec:**

```bash
cat > specs/myapi.yaml << 'YAML'
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /data:
    get:
      operationId: getData
      summary: Get data
      responses:
        '200':
          description: Success
YAML
```

2. **Regenerate Tools:**

```bash
python -m codegen.generator
```

3. **Verify Generation:**

```bash
# Check the generated file
cat server/generated_myapi_tools.py

# Run tests
pytest tests/ -v
```

4. **Test the Server:**

```bash
python -m server.main
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_codegen.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=codegen --cov=server --cov-report=html
```

## CI/CD Integration

The GitHub Actions workflow automatically:

1. Regenerates tools on every push
2. Formats code with Black
3. Lints with Ruff
4. Runs tests
5. Commits generated tools (if changed)
6. Builds and pushes Docker image

### Triggering the Workflow

```bash
# Automatic on push to main
git push origin main

# Manual trigger
gh workflow run ci-cd.yml
```

## Troubleshooting

### Issue: "No generated tool files found"

**Solution:**
```bash
python -m codegen.generator
```

### Issue: Import errors

**Solution:**
```bash
pip install -e ".[dev]"
```

### Issue: Tests failing

**Solution:**
```bash
# Regenerate tools
python -m codegen.generator

# Format code
black codegen/ server/ tests/

# Run tests again
pytest tests/ -v
```

## Advanced Usage

### Custom Type Mappings

To add support for custom types, modify `codegen/generator.py`:

```python
def get_parameter_type(param_schema: Dict[str, Any]) -> str:
    type_mapping = {
        "string": "str",
        "integer": "int",
        # Add your custom types here
        "custom_type": "MyCustomType",
    }
    # ...
```

### Custom Response Handling

Generated tools return text content by default. To customize:

```python
# In generated tools, modify the return statement:
return [
    types.TextContent(
        type="text",
        text=json.dumps(result, indent=2),  # Pretty print JSON
    )
]
```

## Best Practices

1. **Keep specs organized**: One file per service
2. **Use descriptive operation IDs**: They become function names
3. **Include descriptions**: They become docstrings
4. **Test after generation**: Always run tests after regenerating
5. **Version your specs**: Use semantic versioning in spec info
6. **Commit generated files**: So CI/CD can track changes

## Example Project Structure

```
my-cortex-mcp/
├── specs/
│   ├── xsiam.yaml          # Production XSIAM spec
│   ├── xsoar.yaml          # Production XSOAR spec
│   ├── custom-api.yaml     # Your custom API
│   └── dev/                # Development/test specs
│       └── mock-api.yaml
├── server/
│   ├── generated_xsiam_tools.py
│   ├── generated_xsoar_tools.py
│   ├── generated_custom_api_tools.py
│   └── main.py
└── tests/
    ├── test_codegen.py
    ├── test_server.py
    └── test_custom_tools.py
```

