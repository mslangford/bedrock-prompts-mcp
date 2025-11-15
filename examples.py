#!/usr/bin/env python3
"""
Example usage script for Bedrock Prompts MCP Server
Demonstrates all available features
"""

import json
from bedrock_prompts_mcp_server import (
    init_aws_clients,
    list_prompts,
    get_prompt_details,
    invoke_prompt,
    invoke_prompt_stream,
    batch_invoke_prompt,
    list_prompt_versions,
)


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")


def example_list_prompts():
    """Example: List all available prompts"""
    print_section("1. List Available Prompts")
    
    result = list_prompts(max_results=10)
    
    if result["success"]:
        print(f"Found {len(result['prompts'])} prompts:")
        for prompt in result["prompts"]:
            print(f"  - {prompt['name']} ({prompt['id']})")
            print(f"    Description: {prompt.get('description', 'N/A')}")
            print(f"    Version: {prompt.get('version', 'N/A')}")
    else:
        print(f"Error: {result['error']}")
    
    return result.get("prompts", [])


def example_get_prompt_details(prompt_id: str):
    """Example: Get detailed information about a prompt"""
    print_section(f"2. Get Prompt Details: {prompt_id}")
    
    result = get_prompt_details(prompt_id)
    
    if result["success"]:
        prompt = result["prompt"]
        print(f"Name: {prompt.get('name')}")
        print(f"Description: {prompt.get('description')}")
        print(f"Default Variant: {prompt.get('defaultVariant')}")
        
        # Show template variables
        variants = prompt.get("variants", [])
        if variants:
            template_config = variants[0].get("templateConfiguration", {})
            input_vars = template_config.get("text", {}).get("inputVariables", [])
            if input_vars:
                print(f"Required Variables: {[v['name'] for v in input_vars]}")
    else:
        print(f"Error: {result['error']}")


def example_invoke_prompt(prompt_id: str):
    """Example: Invoke a prompt with variables"""
    print_section(f"3. Invoke Prompt: {prompt_id}")
    
    variables = {
        "question": "How do you feel about the economy?"
    }
    
    result = invoke_prompt(prompt_id, variables)
    
    if result["success"]:
        print(f"Model: {result['model_id']} ({result.get('model_type', 'unknown')})")
        print(f"\nCompletion:\n{result['completion']}")
        
        # Show metadata if available
        metadata = result.get("metadata", {})
        if metadata and "response_body" in metadata:
            resp_body = metadata["response_body"]
            if "usage" in resp_body:
                usage = resp_body["usage"]
                print(f"\nToken Usage:")
                print(f"  Input: {usage.get('input_tokens', 'N/A')}")
                print(f"  Output: {usage.get('output_tokens', 'N/A')}")
    else:
        print(f"Error: {result['error']}")


def example_batch_invoke(prompt_id: str):
    """Example: Batch invoke a prompt with multiple variable sets"""
    print_section(f"4. Batch Invoke Prompt: {prompt_id}")
    
    variable_sets = [
        {"question": "How do you feel about the economy?"},
        {"question": "What are your hiring plans for next quarter?"},
        {"question": "How do you view current inflation levels?"},
        {"question": "What challenges is your business facing?"},
        {"question": "How confident are you about the next 6 months?"},
    ]
    
    print(f"Running {len(variable_sets)} invocations in parallel...")
    
    result = batch_invoke_prompt(
        prompt_id,
        variable_sets,
        max_workers=3  # Limit to 3 parallel workers
    )
    
    if result["success"]:
        print(f"\nResults:")
        print(f"  Total: {result['total_invocations']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        
        # Show first few completions
        print(f"\nSample Responses:")
        for i, res in enumerate(result["results"][:2], 1):
            print(f"\n  Response {i}:")
            print(f"  Question: {res['variables']['question']}")
            completion = res['result']['completion']
            # Truncate long responses
            preview = completion[:200] + "..." if len(completion) > 200 else completion
            print(f"  Answer: {preview}")
    else:
        print(f"Error: {result['error']}")


def example_streaming_invoke(prompt_id: str):
    """Example: Invoke a prompt with streaming"""
    print_section(f"5. Stream Prompt Response: {prompt_id}")
    
    variables = {
        "question": "Explain your business strategy in detail."
    }
    
    print("Invoking with streaming enabled...")
    
    result = invoke_prompt_stream(prompt_id, variables)
    
    if result["success"]:
        print(f"\nModel: {result['model_id']} ({result.get('model_type', 'unknown')})")
        print(f"Received {result['chunk_count']} chunks")
        print(f"\nFull Completion:\n{result['completion']}")
    else:
        print(f"Error: {result['error']}")


def example_list_versions(prompt_id: str):
    """Example: List all versions of a prompt"""
    print_section(f"6. List Prompt Versions: {prompt_id}")
    
    result = list_prompt_versions(prompt_id)
    
    if result["success"]:
        versions = result["versions"]
        print(f"Found {len(versions)} version(s):")
        for version in versions:
            print(f"  - Version: {version.get('version', 'DRAFT')}")
            print(f"    Created: {version.get('createdAt', 'N/A')}")
            print(f"    Updated: {version.get('updatedAt', 'N/A')}")
    else:
        print(f"Error: {result['error']}")


def main():
    """Run all examples"""
    print("="*60)
    print("Bedrock Prompts MCP Server - Example Usage")
    print("="*60)
    
    # Initialize AWS clients
    if not init_aws_clients():
        print("Failed to initialize AWS clients. Exiting.")
        return
    
    # 1. List prompts
    prompts = example_list_prompts()
    
    if not prompts:
        print("\nNo prompts found. Please create a prompt in Bedrock first.")
        return
    
    # Use the first prompt for examples
    prompt_id = prompts[0]["id"]
    
    # 2. Get prompt details
    example_get_prompt_details(prompt_id)
    
    # 3. Simple invoke
    example_invoke_prompt(prompt_id)
    
    # 4. Batch invoke (generate multiple responses)
    example_batch_invoke(prompt_id)
    
    # 5. Streaming invoke
    example_streaming_invoke(prompt_id)
    
    # 6. List versions
    example_list_versions(prompt_id)
    
    print_section("Examples Complete")
    print("All examples executed successfully!")


if __name__ == "__main__":
    main()
