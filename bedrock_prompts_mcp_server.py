#!/usr/bin/env python3
"""
MCP Server for AWS Bedrock Managed Prompts

This server provides tools to:
1. List available Bedrock prompts
2. Get prompt details and versions
3. Invoke prompts with variables
4. Batch invoke prompts
5. Stream prompt responses
6. Support for multiple model types (Claude, Titan, Llama, Mistral, etc.)
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, AsyncIterator
from concurrent.futures import ThreadPoolExecutor
import time

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bedrock-prompts-mcp")

# AWS clients
bedrock_agent_client = None
bedrock_runtime_client = None

# Default AWS region from environment or fallback
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DEFAULT_TENANT_ID = os.environ.get("BEDROCK_TENANT_ID", "")


def init_aws_clients():
    """Initialize AWS clients with proper error handling"""
    global bedrock_agent_client, bedrock_runtime_client
    
    try:
        bedrock_agent_client = boto3.client("bedrock-agent", region_name=AWS_REGION)
        bedrock_runtime_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        logger.info(f"AWS clients initialized for region: {AWS_REGION}")
        return True
    except NoCredentialsError:
        logger.error("AWS credentials not found. Please configure AWS credentials.")
        return False
    except Exception as e:
        logger.error(f"Error initializing AWS clients: {e}")
        return False


def get_model_type(model_id: str) -> str:
    """Detect the model type from the model ID"""
    model_id_lower = model_id.lower()
    
    if "claude" in model_id_lower or "anthropic" in model_id_lower:
        return "claude"
    elif "titan" in model_id_lower:
        return "titan"
    elif "llama" in model_id_lower or "meta" in model_id_lower:
        return "llama"
    elif "mistral" in model_id_lower:
        return "mistral"
    elif "cohere" in model_id_lower:
        return "cohere"
    elif "ai21" in model_id_lower or "jurassic" in model_id_lower:
        return "ai21"
    else:
        return "unknown"


def build_request_body_claude(
    filled_template: str,
    inference_config: Dict[str, Any],
    additional_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request body for Claude models"""
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": int(inference_config.get("maxTokens", 2000)),
        "temperature": float(inference_config.get("temperature", 1.0)),
        "top_p": float(inference_config.get("topP", 0.999)),
        "messages": [
            {
                "role": "user",
                "content": filled_template
            }
        ]
    }
    
    if "top_k" in additional_fields:
        request_body["top_k"] = int(additional_fields["top_k"])
    
    stop_sequences = inference_config.get("stopSequences", [])
    if stop_sequences:
        request_body["stop_sequences"] = stop_sequences
    
    return request_body


def build_request_body_titan(
    filled_template: str,
    inference_config: Dict[str, Any],
    additional_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request body for Amazon Titan models"""
    return {
        "inputText": filled_template,
        "textGenerationConfig": {
            "maxTokenCount": int(inference_config.get("maxTokens", 2000)),
            "temperature": float(inference_config.get("temperature", 1.0)),
            "topP": float(inference_config.get("topP", 0.999)),
            "stopSequences": inference_config.get("stopSequences", [])
        }
    }


def build_request_body_llama(
    filled_template: str,
    inference_config: Dict[str, Any],
    additional_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request body for Meta Llama models"""
    return {
        "prompt": filled_template,
        "max_gen_len": int(inference_config.get("maxTokens", 2000)),
        "temperature": float(inference_config.get("temperature", 1.0)),
        "top_p": float(inference_config.get("topP", 0.999))
    }


def build_request_body_mistral(
    filled_template: str,
    inference_config: Dict[str, Any],
    additional_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request body for Mistral AI models"""
    return {
        "prompt": filled_template,
        "max_tokens": int(inference_config.get("maxTokens", 2000)),
        "temperature": float(inference_config.get("temperature", 1.0)),
        "top_p": float(inference_config.get("topP", 0.999)),
        "stop": inference_config.get("stopSequences", [])
    }


def build_request_body_cohere(
    filled_template: str,
    inference_config: Dict[str, Any],
    additional_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request body for Cohere models"""
    return {
        "prompt": filled_template,
        "max_tokens": int(inference_config.get("maxTokens", 2000)),
        "temperature": float(inference_config.get("temperature", 1.0)),
        "p": float(inference_config.get("topP", 0.999)),
        "stop_sequences": inference_config.get("stopSequences", [])
    }


def build_request_body_ai21(
    filled_template: str,
    inference_config: Dict[str, Any],
    additional_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request body for AI21 Labs models"""
    return {
        "prompt": filled_template,
        "maxTokens": int(inference_config.get("maxTokens", 2000)),
        "temperature": float(inference_config.get("temperature", 1.0)),
        "topP": float(inference_config.get("topP", 0.999)),
        "stopSequences": inference_config.get("stopSequences", [])
    }


def parse_response_claude(response_body: Dict[str, Any]) -> str:
    """Parse response from Claude models"""
    return response_body.get("content", [{}])[0].get("text", "")


def parse_response_titan(response_body: Dict[str, Any]) -> str:
    """Parse response from Titan models"""
    results = response_body.get("results", [{}])
    if results:
        return results[0].get("outputText", "")
    return ""


def parse_response_llama(response_body: Dict[str, Any]) -> str:
    """Parse response from Llama models"""
    return response_body.get("generation", "")


def parse_response_mistral(response_body: Dict[str, Any]) -> str:
    """Parse response from Mistral models"""
    outputs = response_body.get("outputs", [{}])
    if outputs:
        return outputs[0].get("text", "")
    return ""


def parse_response_cohere(response_body: Dict[str, Any]) -> str:
    """Parse response from Cohere models"""
    generations = response_body.get("generations", [{}])
    if generations:
        return generations[0].get("text", "")
    return ""


def parse_response_ai21(response_body: Dict[str, Any]) -> str:
    """Parse response from AI21 models"""
    completions = response_body.get("completions", [{}])
    if completions:
        return completions[0].get("data", {}).get("text", "")
    return ""


def build_request_body(
    model_id: str,
    filled_template: str,
    inference_config: Dict[str, Any],
    additional_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """Build request body based on model type"""
    model_type = get_model_type(model_id)
    
    builders = {
        "claude": build_request_body_claude,
        "titan": build_request_body_titan,
        "llama": build_request_body_llama,
        "mistral": build_request_body_mistral,
        "cohere": build_request_body_cohere,
        "ai21": build_request_body_ai21,
    }
    
    builder = builders.get(model_type, build_request_body_claude)
    return builder(filled_template, inference_config, additional_fields)


def parse_model_response(model_id: str, response_body: Dict[str, Any]) -> str:
    """Parse model response based on model type"""
    model_type = get_model_type(model_id)
    
    parsers = {
        "claude": parse_response_claude,
        "titan": parse_response_titan,
        "llama": parse_response_llama,
        "mistral": parse_response_mistral,
        "cohere": parse_response_cohere,
        "ai21": parse_response_ai21,
    }
    
    parser = parsers.get(model_type, parse_response_claude)
    return parser(response_body)



    """List available Bedrock prompts"""
    try:
        params = {"maxResults": max_results}
        if next_token:
            params["nextToken"] = next_token
            
        response = bedrock_agent_client.list_prompts(**params)
        
        return {
            "success": True,
            "prompts": response.get("promptSummaries", []),
            "nextToken": response.get("nextToken"),
        }
    except ClientError as e:
        logger.error(f"AWS API error listing prompts: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        return {"success": False, "error": str(e)}


def get_prompt_details(prompt_identifier: str, prompt_version: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a specific prompt"""
    try:
        params = {"promptIdentifier": prompt_identifier}
        if prompt_version:
            params["promptVersion"] = prompt_version
            
        response = bedrock_agent_client.get_prompt(**params)
        
        return {
            "success": True,
            "prompt": response,
        }
    except ClientError as e:
        logger.error(f"AWS API error getting prompt details: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error getting prompt details: {e}")
        return {"success": False, "error": str(e)}


def invoke_prompt(
    prompt_identifier: str,
    prompt_variables: Optional[Dict[str, str]] = None,
    prompt_version: Optional[str] = None,
    stream: bool = False,
) -> Dict[str, Any]:
    """
    Invoke a Bedrock managed prompt with variables
    
    This function:
    1. Gets the prompt details to extract template and model config
    2. Substitutes variables in the template
    3. Invokes the model with the filled template
    """
    try:
        # Get prompt details
        prompt_details_response = get_prompt_details(prompt_identifier, prompt_version)
        if not prompt_details_response["success"]:
            return prompt_details_response
        
        prompt_data = prompt_details_response["prompt"]
        
        # Get the default variant (or first variant)
        default_variant_name = prompt_data.get("defaultVariant", "variantOne")
        variants = prompt_data.get("variants", [])
        
        variant = None
        for v in variants:
            if v.get("name") == default_variant_name:
                variant = v
                break
        
        if not variant and variants:
            variant = variants[0]
        
        if not variant:
            return {"success": False, "error": "No variant found in prompt"}
        
        # Extract template and config
        template_config = variant.get("templateConfiguration", {})
        template_text = template_config.get("text", {}).get("text", "")
        
        if not template_text:
            return {"success": False, "error": "No template text found in prompt"}
        
        # Substitute variables in template
        filled_template = template_text
        if prompt_variables:
            for var_name, var_value in prompt_variables.items():
                # Support both {{var}} and {var} syntax
                filled_template = filled_template.replace(f"{{{{{var_name}}}}}", var_value)
                filled_template = filled_template.replace(f"{{{var_name}}}", var_value)
        
        # Extract model config
        model_id = variant.get("modelId", "")
        inference_config = variant.get("inferenceConfiguration", {}).get("text", {})
        additional_fields = variant.get("additionalModelRequestFields", {})
        
        # Build request body based on model type
        request_body = build_request_body(
            model_id,
            filled_template,
            inference_config,
            additional_fields
        )
        
        # Invoke the model
        if stream:
            # Streaming not fully supported in sync function, return note
            return {
                "success": False,
                "error": "Streaming requires use of invoke_prompt_stream tool"
            }
        
        response = bedrock_runtime_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response based on model type
        response_body = json.loads(response["body"].read())
        completion_text = parse_model_response(model_id, response_body)
        
        return {
            "success": True,
            "completion": completion_text,
            "model_id": model_id,
            "model_type": get_model_type(model_id),
            "prompt_id": prompt_identifier,
            "filled_template": filled_template,
            "metadata": {
                "response_body": response_body,
            }
        }
        
    except ClientError as e:
        logger.error(f"AWS API error invoking prompt: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error invoking prompt: {e}")
        return {"success": False, "error": str(e)}


def list_prompt_versions(prompt_identifier: str, max_results: int = 20) -> Dict[str, Any]:
    """List all versions of a specific prompt"""
    try:
        response = bedrock_agent_client.list_prompt_versions(
            promptIdentifier=prompt_identifier,
            maxResults=max_results
        )
        
        return {
            "success": True,
            "versions": response.get("promptSummaries", []),
            "nextToken": response.get("nextToken"),
        }
    except ClientError as e:
        logger.error(f"AWS API error listing prompt versions: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error listing prompt versions: {e}")
        return {"success": False, "error": str(e)}


def invoke_prompt_stream(
    prompt_identifier: str,
    prompt_variables: Optional[Dict[str, str]] = None,
    prompt_version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Invoke a Bedrock prompt with streaming response
    Returns chunks of text as they're generated
    """
    try:
        # Get prompt details and build request (reuse logic from invoke_prompt)
        prompt_details_response = get_prompt_details(prompt_identifier, prompt_version)
        if not prompt_details_response["success"]:
            return prompt_details_response
        
        prompt_data = prompt_details_response["prompt"]
        default_variant_name = prompt_data.get("defaultVariant", "variantOne")
        variants = prompt_data.get("variants", [])
        
        variant = None
        for v in variants:
            if v.get("name") == default_variant_name:
                variant = v
                break
        
        if not variant and variants:
            variant = variants[0]
        
        if not variant:
            return {"success": False, "error": "No variant found in prompt"}
        
        template_config = variant.get("templateConfiguration", {})
        template_text = template_config.get("text", {}).get("text", "")
        
        if not template_text:
            return {"success": False, "error": "No template text found in prompt"}
        
        # Substitute variables
        filled_template = template_text
        if prompt_variables:
            for var_name, var_value in prompt_variables.items():
                filled_template = filled_template.replace(f"{{{{{var_name}}}}}", var_value)
                filled_template = filled_template.replace(f"{{{var_name}}}", var_value)
        
        # Extract model config
        model_id = variant.get("modelId", "")
        inference_config = variant.get("inferenceConfiguration", {}).get("text", {})
        additional_fields = variant.get("additionalModelRequestFields", {})
        
        # Build request body
        request_body = build_request_body(
            model_id,
            filled_template,
            inference_config,
            additional_fields
        )
        
        # Invoke with streaming
        response = bedrock_runtime_client.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Collect streamed chunks
        full_text = ""
        chunks = []
        
        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_obj = json.loads(chunk.get('bytes').decode())
                    
                    # Parse based on model type
                    model_type = get_model_type(model_id)
                    
                    if model_type == "claude":
                        # Claude streaming format
                        if chunk_obj.get('type') == 'content_block_delta':
                            delta = chunk_obj.get('delta', {})
                            text = delta.get('text', '')
                            if text:
                                full_text += text
                                chunks.append(text)
                    elif model_type == "titan":
                        # Titan streaming format
                        text = chunk_obj.get('outputText', '')
                        if text:
                            full_text += text
                            chunks.append(text)
                    else:
                        # Generic fallback
                        text = str(chunk_obj)
                        full_text += text
                        chunks.append(text)
        
        return {
            "success": True,
            "completion": full_text,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "model_id": model_id,
            "model_type": get_model_type(model_id),
            "prompt_id": prompt_identifier,
        }
        
    except ClientError as e:
        logger.error(f"AWS API error streaming prompt: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error streaming prompt: {e}")
        return {"success": False, "error": str(e)}


def batch_invoke_prompt(
    prompt_identifier: str,
    variable_sets: List[Dict[str, str]],
    prompt_version: Optional[str] = None,
    max_workers: int = 5,
) -> Dict[str, Any]:
    """
    Invoke a prompt multiple times with different variable sets
    Runs invocations in parallel for efficiency
    
    Args:
        prompt_identifier: Prompt ID to invoke
        variable_sets: List of variable dictionaries, one per invocation
        prompt_version: Optional version to use
        max_workers: Maximum parallel workers (default: 5)
    """
    try:
        results = []
        errors = []
        
        def invoke_single(variables: Dict[str, str], index: int) -> Dict[str, Any]:
            """Single invocation wrapper"""
            try:
                result = invoke_prompt(prompt_identifier, variables, prompt_version)
                return {
                    "index": index,
                    "variables": variables,
                    "result": result,
                    "success": result.get("success", False),
                }
            except Exception as e:
                return {
                    "index": index,
                    "variables": variables,
                    "success": False,
                    "error": str(e),
                }
        
        # Use ThreadPoolExecutor for parallel invocations
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(invoke_single, var_set, i)
                for i, var_set in enumerate(variable_sets)
            ]
            
            for future in futures:
                try:
                    result = future.result(timeout=120)  # 2 minute timeout per call
                    if result["success"]:
                        results.append(result)
                    else:
                        errors.append(result)
                except Exception as e:
                    errors.append({
                        "success": False,
                        "error": f"Future execution error: {str(e)}"
                    })
        
        return {
            "success": True,
            "total_invocations": len(variable_sets),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
            "prompt_id": prompt_identifier,
        }
        
    except Exception as e:
        logger.error(f"Error in batch invocation: {e}")
        return {"success": False, "error": str(e)}


# Create MCP server instance
app = Server("bedrock-prompts")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for Bedrock prompt management"""
    return [
        Tool(
            name="list_bedrock_prompts",
            description="List available AWS Bedrock managed prompts. Returns prompt summaries including ID, name, description, and version info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of prompts to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                    },
                    "next_token": {
                        "type": "string",
                        "description": "Token for pagination to get next page of results",
                    },
                },
            },
        ),
        Tool(
            name="get_bedrock_prompt_details",
            description="Get detailed information about a specific Bedrock prompt including template, variables, model configuration, and inference settings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_identifier": {
                        "type": "string",
                        "description": "The prompt ID or ARN to retrieve",
                    },
                    "prompt_version": {
                        "type": "string",
                        "description": "Specific version of the prompt (optional, defaults to DRAFT)",
                    },
                },
                "required": ["prompt_identifier"],
            },
        ),
        Tool(
            name="invoke_bedrock_prompt",
            description="Invoke a Bedrock managed prompt with variables and get the model's response. Automatically handles template substitution and model invocation. Supports Claude, Titan, Llama, Mistral, Cohere, and AI21 models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_identifier": {
                        "type": "string",
                        "description": "The prompt ID or ARN to invoke",
                    },
                    "prompt_variables": {
                        "type": "object",
                        "description": "Dictionary of variable names to values for template substitution (e.g., {'question': 'How are you?'})",
                        "additionalProperties": {"type": "string"},
                    },
                    "prompt_version": {
                        "type": "string",
                        "description": "Specific version of the prompt to invoke (optional, defaults to DRAFT)",
                    },
                },
                "required": ["prompt_identifier"],
            },
        ),
        Tool(
            name="invoke_bedrock_prompt_stream",
            description="Invoke a Bedrock prompt with streaming response. Returns text chunks as they're generated. Best for long-form content or when you want to see incremental progress.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_identifier": {
                        "type": "string",
                        "description": "The prompt ID or ARN to invoke",
                    },
                    "prompt_variables": {
                        "type": "object",
                        "description": "Dictionary of variable names to values for template substitution",
                        "additionalProperties": {"type": "string"},
                    },
                    "prompt_version": {
                        "type": "string",
                        "description": "Specific version of the prompt to invoke (optional, defaults to DRAFT)",
                    },
                },
                "required": ["prompt_identifier"],
            },
        ),
        Tool(
            name="batch_invoke_bedrock_prompt",
            description="Invoke a Bedrock prompt multiple times with different variable sets. Runs invocations in parallel for efficiency. Perfect for generating multiple survey responses, variations, or test cases.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_identifier": {
                        "type": "string",
                        "description": "The prompt ID or ARN to invoke",
                    },
                    "variable_sets": {
                        "type": "array",
                        "description": "Array of variable dictionaries, one per invocation. Example: [{'question': 'Q1'}, {'question': 'Q2'}]",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                    },
                    "prompt_version": {
                        "type": "string",
                        "description": "Specific version of the prompt to invoke (optional, defaults to DRAFT)",
                    },
                    "max_workers": {
                        "type": "integer",
                        "description": "Maximum number of parallel workers (1-10, default: 5)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5,
                    },
                },
                "required": ["prompt_identifier", "variable_sets"],
            },
        ),
        Tool(
            name="list_bedrock_prompt_versions",
            description="List all versions of a specific Bedrock prompt, showing version history and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_identifier": {
                        "type": "string",
                        "description": "The prompt ID or ARN to get versions for",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of versions to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                    },
                },
                "required": ["prompt_identifier"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls for Bedrock prompt operations"""
    
    try:
        if name == "list_bedrock_prompts":
            max_results = arguments.get("max_results", 20)
            next_token = arguments.get("next_token")
            result = list_prompts(max_results, next_token)
            
        elif name == "get_bedrock_prompt_details":
            prompt_identifier = arguments["prompt_identifier"]
            prompt_version = arguments.get("prompt_version")
            result = get_prompt_details(prompt_identifier, prompt_version)
            
        elif name == "invoke_bedrock_prompt":
            prompt_identifier = arguments["prompt_identifier"]
            prompt_variables = arguments.get("prompt_variables")
            prompt_version = arguments.get("prompt_version")
            result = invoke_prompt(prompt_identifier, prompt_variables, prompt_version)
            
        elif name == "invoke_bedrock_prompt_stream":
            prompt_identifier = arguments["prompt_identifier"]
            prompt_variables = arguments.get("prompt_variables")
            prompt_version = arguments.get("prompt_version")
            result = invoke_prompt_stream(prompt_identifier, prompt_variables, prompt_version)
            
        elif name == "batch_invoke_bedrock_prompt":
            prompt_identifier = arguments["prompt_identifier"]
            variable_sets = arguments["variable_sets"]
            prompt_version = arguments.get("prompt_version")
            max_workers = arguments.get("max_workers", 5)
            result = batch_invoke_prompt(
                prompt_identifier,
                variable_sets,
                prompt_version,
                max_workers
            )
            
        elif name == "list_bedrock_prompt_versions":
            prompt_identifier = arguments["prompt_identifier"]
            max_results = arguments.get("max_results", 20)
            result = list_prompt_versions(prompt_identifier, max_results)
            
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        
        # Format response
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        error_result = {"success": False, "error": str(e)}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main():
    """Main entry point for the MCP server"""
    # Initialize AWS clients
    if not init_aws_clients():
        logger.error("Failed to initialize AWS clients. Exiting.")
        return
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Bedrock Prompts MCP Server starting...")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
