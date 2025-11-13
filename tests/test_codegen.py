"""Tests for the code generator."""

import tempfile
from pathlib import Path

import yaml

from codegen.generator import (
    generate_tools_file,
    to_snake_case,
    strip_http_verb_prefix,
    clean_public_api_name,
    get_parameter_type,
    generate_parameter_schema,
)


def test_strip_http_verb_prefix():
    """Test HTTP verb prefix stripping based on HTTP method."""
    # Test POST prefix stripping when method is POST
    assert strip_http_verb_prefix("postStartXqlQuery", "post") == "StartXqlQuery"
    assert strip_http_verb_prefix("postGetQueryResults", "post") == "GetQueryResults"
    assert strip_http_verb_prefix("postUpdateIncident", "post") == "UpdateIncident"

    # Test GET prefix stripping when method is GET
    assert strip_http_verb_prefix("getIncidents", "get") == "Incidents"
    assert strip_http_verb_prefix("getAutomationScripts", "get") == "AutomationScripts"

    # Test PUT prefix stripping when method is PUT
    assert strip_http_verb_prefix("putUpdateUser", "put") == "UpdateUser"

    # Test PATCH prefix stripping when method is PATCH
    assert strip_http_verb_prefix("patchModifyIncident", "patch") == "ModifyIncident"

    # Test DELETE prefix stripping when method is DELETE
    assert strip_http_verb_prefix("deleteRemoveAlert", "delete") == "RemoveAlert"

    # Test with hyphens
    assert (
        strip_http_verb_prefix("post-public_api-v1-alerts-get_alerts", "post")
        == "-public_api-v1-alerts-get_alerts"
    )

    # Test no stripping when prefix doesn't match method
    assert strip_http_verb_prefix("getAutomationScripts", "post") == "getAutomationScripts"
    assert strip_http_verb_prefix("postGetIncidents", "get") == "postGetIncidents"

    # Test no prefix (should remain unchanged)
    assert strip_http_verb_prefix("listIncidents", "post") == "listIncidents"
    assert strip_http_verb_prefix("createIncident", "post") == "createIncident"
    assert strip_http_verb_prefix("executePlaybook", "get") == "executePlaybook"

    # Test edge case: verb as whole word (should not strip)
    assert strip_http_verb_prefix("getter", "get") == "getter"
    assert strip_http_verb_prefix("poster", "post") == "poster"

    # Test without method parameter
    assert strip_http_verb_prefix("postStartXqlQuery", "") == "postStartXqlQuery"
    assert strip_http_verb_prefix("getIncidents", "") == "getIncidents"


def test_clean_public_api_name():
    """Test cleaning public_api names by moving version to end."""
    # Test v1 API
    assert clean_public_api_name("public_api-v1-alerts-get_alerts") == "alerts-get_alerts-v1"

    # Test v2 API
    assert (
        clean_public_api_name("public_api-v2-alerts-get_alerts_multi_events")
        == "alerts-get_alerts_multi_events-v2"
    )

    # Test with leading hyphen (from HTTP verb stripping)
    assert clean_public_api_name("-public_api-v1-alerts-get_alerts") == "alerts-get_alerts-v1"
    assert (
        clean_public_api_name("-public_api-v2-alerts-get_alerts_multi_events")
        == "alerts-get_alerts_multi_events-v2"
    )

    # Test non-public_api names (should remain unchanged)
    assert clean_public_api_name("startXqlQuery") == "startXqlQuery"
    assert clean_public_api_name("getIncidents") == "getIncidents"

    # Test public_api without version (edge case)
    assert clean_public_api_name("public_api-alerts-get_alerts") == "alerts-get_alerts"


def test_to_snake_case():
    """Test snake_case conversion."""
    # Basic conversions without HTTP method
    assert to_snake_case("listIncidents") == "list_incidents"
    assert to_snake_case("createIncident") == "create_incident"
    assert to_snake_case("executePlaybook") == "execute_playbook"

    # Test with HTTP method matching (should strip prefix)
    assert to_snake_case("postStartXqlQuery", "post") == "start_xql_query"
    assert to_snake_case("postGetQueryResults", "post") == "get_query_results"
    assert to_snake_case("getIncidents", "get") == "incidents"
    assert to_snake_case("postUpdateIncident", "post") == "update_incident"
    assert to_snake_case("deleteWidget", "delete") == "widget"

    # Test public_api name cleaning
    assert to_snake_case("public_api-v1-alerts-get_alerts", "post") == "alerts_get_alerts_v1"
    assert (
        to_snake_case("public_api-v2-alerts-get_alerts_multi_events", "post")
        == "alerts_get_alerts_multi_events_v2"
    )

    # Test with HTTP method not matching (should not strip)
    assert to_snake_case("getAutomationScripts", "post") == "get_automation_scripts"
    assert to_snake_case("getIncidentID", "post") == "get_incident_id"


def test_get_parameter_type():
    """Test parameter type mapping."""
    assert get_parameter_type({"type": "string"}) == "str"
    assert get_parameter_type({"type": "integer"}) == "int"
    assert get_parameter_type({"type": "number"}) == "float"
    assert get_parameter_type({"type": "boolean"}) == "bool"
    assert get_parameter_type({"type": "array"}) == "List[Any]"
    assert get_parameter_type({"type": "object"}) == "Dict[str, Any]"


def test_generate_parameter_schema():
    """Test parameter schema generation."""
    parameters = [
        {
            "name": "limit",
            "in": "query",
            "required": False,
            "schema": {"type": "integer"},
            "description": "Maximum number of results",
        },
        {
            "name": "status",
            "in": "query",
            "required": True,
            "schema": {"type": "string"},
            "description": "Filter by status",
        },
    ]

    param_defs, schema_props, param_info = generate_parameter_schema(parameters)

    assert len(param_defs) == 2
    # Required params come first now
    assert "status: str," in param_defs[0]
    assert "limit: int | None = None," in param_defs[1]

    assert len(schema_props) == 2
    assert '"limit"' in schema_props[0] or '"limit"' in schema_props[1]
    assert '"status"' in schema_props[0] or '"status"' in schema_props[1]

    # Check param_info
    assert len(param_info) == 2
    assert any(p["name"] == "limit" and not p["required"] for p in param_info)
    assert any(p["name"] == "status" and p["required"] for p in param_info)


def test_generate_tools_file():
    """Test generating a tools file from a spec."""
    # Create a minimal OpenAPI spec
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "servers": [{"url": "https://api.test.com"}],
        "paths": {
            "/items": {
                "get": {
                    "operationId": "listItems",
                    "summary": "List items",
                    "description": "Get all items",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Max items",
                        }
                    ],
                    "responses": {"200": {"description": "Success"}},
                }
            }
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_path = Path(tmpdir) / "test.yaml"
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        # Write the spec
        with open(spec_path, "w") as f:
            yaml.dump(spec, f)

        # Generate the tools file
        generate_tools_file(spec_path, output_dir)

        # Check the output file exists
        output_file = output_dir / "generated_test_tools.py"
        assert output_file.exists()

        # Check the content - now includes service prefix
        content = output_file.read_text()
        assert "def test_list_items" in content
        assert "limit: int | None = None" in content
        assert "async def test_list_items" in content
        assert "@server.call_tool()" in content

        # Check that the docstring has detailed parameter documentation
        assert "Args:" in content
        assert "limit (int): Max items (optional)" in content
        assert "Returns:" in content


def test_docstring_parameter_documentation():
    """Test that generated functions have detailed parameter documentation in docstrings."""
    # Create a spec with multiple parameter types
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "servers": [{"url": "https://api.test.com"}],
        "paths": {
            "/users/{user_id}": {
                "post": {
                    "operationId": "updateUser",
                    "summary": "Update a user",
                    "description": "Updates user information",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "The user ID",
                        },
                        {
                            "name": "notify",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Send notification",
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name"],
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "User's full name",
                                        },
                                        "email": {
                                            "type": "string",
                                            "description": "User's email address",
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"200": {"description": "User updated successfully"}},
                }
            }
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_path = Path(tmpdir) / "test.yaml"
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        with open(spec_path, "w") as f:
            yaml.dump(spec, f)

        generate_tools_file(spec_path, output_dir)

        output_file = output_dir / "generated_test_tools.py"
        content = output_file.read_text()

        # Verify all parameters are documented in the docstring
        assert "user_id (str): The user ID (required)" in content
        assert "notify (bool): Send notification (optional)" in content
        assert "name (str): User's full name (required)" in content
        assert "email (str): User's email address (optional)" in content

        # Verify return documentation includes response description
        assert "User updated successfully" in content


def test_request_data_expansion():
    """Test that request_data wrapper is properly expanded into individual parameters."""
    # Create a spec with request_data wrapper pattern (like XSIAM update_incident)
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "servers": [{"url": "https://api.test.com"}],
        "paths": {
            "/incidents/update": {
                "post": {
                    "operationId": "updateIncident",
                    "summary": "Update an incident",
                    "description": "Updates incident information",
                    "parameters": [
                        {
                            "name": "Authorization",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "API key",
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "request_data": {
                                            "type": "object",
                                            "required": ["incident_id", "update_data"],
                                            "properties": {
                                                "incident_id": {
                                                    "type": "string",
                                                    "description": "The incident ID",
                                                },
                                                "update_data": {
                                                    "type": "object",
                                                    "description": "Data to update",
                                                },
                                                "optional_field": {
                                                    "type": "string",
                                                    "description": "Optional field",
                                                },
                                            },
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"200": {"description": "Success"}},
                }
            }
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        spec_path = Path(tmpdir) / "test.yaml"
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        with open(spec_path, "w") as f:
            yaml.dump(spec, f)

        generate_tools_file(spec_path, output_dir)

        output_file = output_dir / "generated_test_tools.py"
        content = output_file.read_text()

        # Verify that request_data is NOT a parameter
        assert "request_data: Dict[str, Any]" not in content
        assert "request_data (Dict[str, Any])" not in content

        # Verify that nested properties ARE parameters
        assert "incident_id: str," in content
        assert "update_data: Dict[str, Any]," in content
        assert "optional_field: str | None = None," in content

        # Verify documentation shows required/optional correctly
        assert "incident_id (str): The incident ID (required)" in content
        assert "update_data (Dict[str, Any]): Data to update (required)" in content
        assert "optional_field (str): Optional field (optional)" in content

        # Verify the body building code wraps parameters back into request_data
        assert "request_data_obj = {}" in content
        assert 'request_data_obj["incident_id"] = incident_id' in content
        assert 'request_data_obj["update_data"] = update_data' in content
        assert 'request_data_obj["optional_field"] = optional_field' in content
        assert 'body["request_data"] = request_data_obj' in content
