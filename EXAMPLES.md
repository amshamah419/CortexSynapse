# AI-Assisted XSOAR/XSIAM Development Examples

This document provides practical examples of using CortexSynapse with AI-powered IDEs for XSOAR and XSIAM development workflows.

## Prerequisites

- CortexSynapse container running and configured in your AI IDE (Windsurf, Cursor, Roo Code, etc.)
- Active XSOAR and/or XSIAM instance with API credentials
- AI IDE with MCP support enabled

## Tool Documentation Reference

All 213 MCP tools (128 XSIAM + 85 XSOAR) now have comprehensive documentation that includes:
- **What the tool does**: Clear description of the tool's purpose
- **What it expects**: Detailed parameter documentation showing name, type, description, and whether it's required or optional
- **What it returns**: Specific return value descriptions based on the API response

### Example Tool Documentation

Here's an example of the improved documentation for `xsiam_get_incidents`:

```python
async def xsiam_get_incidents(
    authorization: str,
    x_xdr_auth_id: str,
    request_data: Dict[str, Any] | None = None,
) -> List[types.TextContent]:
    """
    Get a list of incidents filtered by a list of incident IDs, modification time, 
    or creation time. This includes all incident types and severities, including 
    correlation-generated incidents.
    
    Args:
        authorization (str): {api_key} (required)
        x_xdr_auth_id (str): {api_key_id} (required)
        request_data (Dict[str, Any]): A dictionary containing the API request 
            fields. An empty dictionary returns all results. (optional)
    
    Returns:
        List[types.TextContent]: Successful response
    """
```

### How to Find Tool Documentation

1. **Browse generated files**: Check `server/generated_xsiam_tools.py` or `server/generated_xsoar_tools.py`
2. **Look for the function name**: Tools are prefixed with `xsiam_` or `xsoar_`
3. **Read the docstring**: Each tool has a comprehensive docstring with all parameters documented

## Common Development Workflows

### Workflow 1: Incident Investigation and Response

**Scenario**: You're investigating a potential security incident and need to gather context quickly.

**Developer to AI**: "Show me all critical incidents from the last 24 hours that involve endpoint 'DESKTOP-12345'"

**What happens**:
1. AI agent calls `xsiam_get_incidents` with the following parameters:
   - `authorization`: Your API key (required)
   - `x_xdr_auth_id`: Your API key ID (required)
   - `request_data`: Dictionary with severity and time filters (optional)
2. Parses results to find incidents mentioning the endpoint
3. Optionally calls `xsiam_get_incident_extra_data` for detailed context
4. Presents findings in natural language with recommendations

**Result**: You get immediate insight without manually navigating the XSIAM UI or writing API calls.

### Workflow 2: XQL Query Development

**Scenario**: You need to develop an XQL query for threat hunting but aren't sure about the exact syntax.

**Developer to AI**: "Write an XQL query to find all authentication failures where the source IP is external in the last 7 days"

**What happens**:
1. AI agent generates appropriate XQL syntax
2. Calls `xsiam_start_xql_query` with the following parameters:
   - `authorization`: Your API key (required)
   - `x_xdr_auth_id`: Your API key ID (required)
   - `request_data`: Dictionary containing the XQL query (required)
3. Uses `xsiam_get_query_results` to retrieve results with:
   - `authorization`: Your API key (required)
   - `x_xdr_auth_id`: Your API key ID (required)
   - `request_data`: Dictionary with the query execution ID (required)
4. Formats and displays findings

**Result**: XQL query development with immediate feedback, no need to context-switch to XSIAM console.

### Workflow 3: Playbook Testing

**Scenario**: You've written a custom playbook and need to test it against various incident types.

**Developer to AI**: "Create 3 test incidents with different severities to test my phishing response playbook"

**What happens**:
1. AI agent calls `post_create_incident` three times with varying parameters
2. Provides incident IDs for tracking
3. Optionally executes playbook with `execute_playbook`
4. Can monitor progress with subsequent queries

**Result**: Rapid playbook iteration without manual incident creation.

### Workflow 4: Automation Script Development

**Scenario**: You're building a custom automation script and need to test it.

**Developer to AI**: "Upload my automation script 'EnrichIPAddress.py' and run it against incident #12345"

**What happens**:
1. AI helps format the script according to XSOAR requirements
2. Calls `xsoar_save_or_update_script` to upload the automation
   - Note: This tool requires no parameters - the script data is provided in the request body
3. Can trigger script execution within investigation context
4. Retrieves results for validation

**Result**: Streamlined automation development cycle.

### Workflow 5: Indicator Management

**Scenario**: You have a list of suspicious IPs that need to be added to your threat intelligence.

**Developer to AI**: "Add these IP addresses as malicious indicators: 192.168.1.100, 10.0.0.50, 172.16.0.20"

**What happens**:
1. AI agent formats the IPs appropriately
2. Calls `xsoar_save_or_update_indicators` with correct indicator type and malicious verdict
   - Parameters are passed in the request body containing indicator details
3. Confirms successful creation
4. Optionally queries to verify with `xsoar_search_indicators`

**Result**: Bulk indicator management without tedious UI clicks.

## Advanced Scenarios

### Multi-Step Investigation Workflow

**Developer to AI**: "Investigate the spike in authentication failures - start with an XQL query, create an incident if threshold is exceeded, and add relevant context"

**AI Agent Workflow**:
```python
# Step 1: Query for auth failures using xsiam_start_xql_query
query = "SELECT source_ip, count() as failures FROM auth_logs WHERE status='failed' AND _time > now() - 1h GROUP BY source_ip"
query_result = xsiam_start_xql_query(
    authorization=api_key,
    x_xdr_auth_id=api_key_id,
    request_data={"query": query}
)

# Step 2: Get results using xsiam_get_query_results
results = xsiam_get_query_results(
    authorization=api_key,
    x_xdr_auth_id=api_key_id,
    request_data={"execution_id": query_result["execution_id"]}
)

# Step 3: Analyze results
if any(result['failures'] > 10 for result in results):
    # Step 4: Create incident using xsiam_update_incident or similar
    incident = xsiam_create_incident(
        authorization=api_key,
        x_xdr_auth_id=api_key_id,
        request_data={
            "name": "Excessive Authentication Failures Detected",
            "severity": "high",
            "description": f"Detected {max_failures} failures from {source_ip}"
        }
    )
    
    # Step 5: Add investigation notes using xsoar_investigation_add_entry_handler
    xsoar_investigation_add_entry_handler(
        request_data={
            "incident_id": incident['id'],
            "entry": "XQL query results indicate potential brute force attack"
        }
    )
```

**Result**: Complete investigation workflow automated through natural language.

### Playbook Development & Deployment

**Developer to AI**: "Help me build a playbook for ransomware response - it should isolate the endpoint, create high severity incident, notify security team, and initiate forensic collection"

**AI Agent Assists With**:
1. Generating playbook structure using XSOAR best practices
2. Testing individual tasks using API calls
3. Deploying and validating the playbook
4. Creating test scenarios to verify each branch

**Result**: Faster playbook development with AI understanding XSOAR playbook patterns.

### Content Pack Development

**Developer to AI**: "List all automation scripts in my 'CustomIntegrations' pack and check if they're following naming conventions"

**AI Agent Actions**:
```python
# Get all scripts using xsoar_get_automation_scripts
scripts_response = xsoar_get_automation_scripts()
scripts = scripts_response  # Parse the response

# Filter by pack
custom_scripts = [s for s in scripts if s.get('pack') == 'CustomIntegrations']

# Validate naming (example check)
for script in custom_scripts:
    if not script['name'].startswith('Custom'):
        print(f"Warning: {script['name']} doesn't follow naming convention")
```

**Result**: Automated content pack quality checks.

## Integration with AI IDEs

### Windsurf Configuration Example

In `.windsurf/mcp.json`:
```json
{
  "mcpServers": {
    "cortex-dev": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "cortexsynapse"],
      "env": {
        "XSOAR_API_URL": "https://xsoar-dev.company.com",
        "XSOAR_API_KEY": "${XSOAR_DEV_KEY}",
        "XSIAM_API_URL": "https://xsiam-dev.company.com",
        "XSIAM_API_KEY": "${XSIAM_DEV_KEY}",
        "XSIAM_API_KEY_ID": "${XSIAM_DEV_KEY_ID}"
      }
    }
  }
}
```

### Cursor Configuration Example

In Cursor settings (Settings → Features → MCP):
```json
{
  "cortex": {
    "command": "docker",
    "args": ["run", "-i", "cortexsynapse"],
    "env": {
      "XSOAR_API_URL": "https://your-instance.xsoar.com",
      "XSOAR_API_KEY": "your-api-key"
    }
  }
}
```

## Tips for Effective AI-Assisted Development

1. **Be Specific**: Instead of "query incidents", say "query critical incidents from last hour"
2. **Iterate**: Start simple, then refine with follow-up requests
3. **Combine Operations**: AI can chain multiple API calls - use this for complex workflows
4. **Verify**: Always review AI-generated API calls before execution on production
5. **Context**: Provide incident IDs, playbook names, or other specific context for better results

## Troubleshooting Common Scenarios

### "Cannot connect to XSOAR instance"
- Check API URL in MCP configuration
- Verify API key is valid and has correct permissions
- Test connectivity: `curl -H "Authorization: YOUR_KEY" https://your-instance/api/v1/health`

### "Tool execution timeout"
- XQL queries on large datasets may take time - use streaming endpoints
- Break complex operations into smaller steps
- Consider pagination for large result sets

### "Unexpected tool behavior"
- Check AI IDE logs for actual API calls being made
- Verify tool parameters match XSOAR/XSIAM API expectations
- Use `--verbose` flag if available to see detailed execution

## Best Practices

1. **Development vs Production**: Use separate MCP configurations for dev and production instances
2. **API Key Security**: Use environment variables, never hardcode keys
3. **Rate Limiting**: Be aware of API rate limits, especially for bulk operations
4. **Testing**: Test playbooks and automations in dev environment first
5. **Version Control**: Keep your MCP configurations in version control (without secrets)

## Real-World Example: Daily Security Review

**Developer**: "Give me a security status update - show critical incidents, recent high-value alerts, and any endpoints that need attention"

**AI Agent Orchestrates**:
```python
# Get critical incidents using xsiam_get_incidents
incidents = xsiam_get_incidents(
    authorization=api_key,
    x_xdr_auth_id=api_key_id,
    request_data={"severity": "critical", "limit": 10}
)

# Get high severity alerts using xsiam_alerts_get_alerts_v1
alerts = xsiam_alerts_get_alerts_v1(
    authorization=api_key,
    x_xdr_auth_id=api_key_id,
    request_data={"severity": "high", "time_range": 24}
)

# Check for isolated endpoints using xsiam_endpoints_get_endpoint
endpoints = xsiam_endpoints_get_endpoint(
    authorization=api_key,
    x_xdr_auth_id=api_key_id,
    request_data={"status": "isolated"}
)

# Format comprehensive report
print(f"""
Security Status Update:
- {len(incidents)} critical incidents requiring attention
- {len(alerts)} high-severity alerts in last 24h
- {len(endpoints)} endpoints currently isolated
[Detailed breakdown...]
""")
```

**Result**: Comprehensive security posture in seconds, not minutes of manual querying.

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
docker build -t cortexsynapse .
```

### Run the Container

```bash
docker run -i cortexsynapse
```

### Push to Registry

```bash
docker tag cortexsynapse ghcr.io/your-username/cortexsynapse:latest
docker push ghcr.io/your-username/cortexsynapse:latest
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
my-cortexsynapse/
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

