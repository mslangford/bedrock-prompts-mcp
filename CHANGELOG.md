# Changelog

All notable changes to the Bedrock Prompts MCP Server.

## [0.2.0] - 2024-11-14

### Added
- **Batch Invocation**: New `batch_invoke_bedrock_prompt` tool for parallel execution
  - Run same prompt with multiple variable sets
  - Configurable parallelism (1-10 workers)
  - Separate tracking of successes/failures
  - Ideal for generating multiple survey responses or testing variations

- **Streaming Support**: New `invoke_bedrock_prompt_stream` tool
  - Real-time text streaming as model generates
  - Returns both chunks and full completion
  - Improved UX for long-form content
  - Works with Claude and Titan models

- **Multi-Model Support**: Automatic detection and formatting for:
  - Amazon Titan (titan-text-express, titan-text-lite)
  - Meta Llama (llama-2, llama-3)
  - Mistral AI (mistral-7b, mixtral-8x7b)
  - Cohere (command, command-light)
  - AI21 Labs (jurassic-2)
  - Anthropic Claude (existing)

- **Model-Specific Request Builders**: 
  - `build_request_body_*()` functions for each model type
  - Automatic detection via `get_model_type()`
  - Correct parameter mapping per model API

- **Model-Specific Response Parsers**:
  - `parse_response_*()` functions for each model type
  - Handles different response formats automatically
  - Extracts text from various response structures

- **Documentation**:
  - `QUICK_REFERENCE.md`: Common use cases and best practices
  - `examples.py`: Runnable examples for all features
  - Enhanced README with batch/streaming examples

### Changed
- `invoke_prompt()` now uses model-agnostic request builder
- Better model ID extraction from Bedrock ARNs
- More detailed response metadata including model type
- Improved error messages with context

### Technical Details
- Added ThreadPoolExecutor for parallel batch processing
- Streaming uses `invoke_model_with_response_stream` API
- Timeout handling (120s per invocation in batch mode)
- Better exception handling across all model types

## [0.1.0] - 2024-11-13

### Added
- Initial MCP server implementation
- `list_bedrock_prompts`: Browse available prompts
- `get_bedrock_prompt_details`: View prompt configuration
- `invoke_bedrock_prompt`: Execute prompts with variables
- `list_bedrock_prompt_versions`: Version management
- Claude Desktop integration
- Basic Claude model support
- Variable substitution ({{var}} and {var} syntax)
- AWS credential handling
- Error handling and logging

### Technical Details
- Python 3.10+ required
- boto3 for AWS SDK
- mcp library for protocol implementation
- stdio-based communication
