# Bedrock Prompts MCP Server

An MCP (Model Context Protocol) server for managing and invoking AWS Bedrock managed prompts.

## Features

- **List Prompts**: Browse all available Bedrock managed prompts
- **Get Prompt Details**: View complete prompt configuration including templates, variables, and model settings
- **Invoke Prompts**: Execute prompts with variable substitution and get model responses
- **Batch Invocation**: Run the same prompt multiple times with different inputs in parallel
- **Streaming Responses**: Get real-time streaming output from prompts (for supported models)
- **Multi-Model Support**: Works with Claude, Amazon Titan, Meta Llama, Mistral AI, Cohere, and AI21 models
- **Version Management**: List and access different versions of prompts

## Prerequisites

- Python 3.10 or higher
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)
- Access to AWS Bedrock service
- Claude Desktop (for MCP integration)

## Installation

### Option 1: Local Development

```bash
# Clone or download the files
cd /path/to/bedrock-prompts-mcp

# Install dependencies
pip install -r requirements.txt

# Test the server
python bedrock_prompts_mcp_server.py
```

### Option 2: Install as Package

```bash
pip install -e .
```

## AWS Configuration

Ensure your AWS credentials are configured. The server will use the default credential chain:

```bash
# Via AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

Optional environment variables:
- `AWS_REGION`: AWS region for Bedrock (default: us-east-1)
- `BEDROCK_TENANT_ID`: Optional tenant identifier

## Claude Desktop Configuration

Add this to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bedrock-prompts": {
      "command": "python",
      "args": ["/absolute/path/to/bedrock_prompts_mcp_server.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

If you installed as a package:

```json
{
  "mcpServers": {
    "bedrock-prompts": {
      "command": "bedrock-prompts-mcp",
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Usage in Claude Desktop

Once configured, you can use natural language to interact with your Bedrock prompts:

### Examples

**List available prompts:**
```
Show me all my Bedrock prompts
```

**Get prompt details:**
```
Get the details for prompt VSWZVOISYG
```

**Invoke a prompt:**
```
Invoke prompt VSWZVOISYG with the question "How do you feel about the economy?"
```

**Generate multiple responses:**
```
Use prompt VSWZVOISYG to generate 5 different survey responses to "How do you feel about the economy?"
```

**Batch invoke with different inputs:**
```
Batch invoke prompt VSWZVOISYG with these questions:
1. "How do you feel about the economy?"
2. "What are your hiring plans?"
3. "How do you view inflation?"
```

**Stream a long response:**
```
Stream the response from prompt VSWZVOISYG with streaming enabled
```

## Available Tools

### 1. list_bedrock_prompts
Lists all available Bedrock managed prompts.

**Parameters:**
- `max_results` (optional): Number of results (1-100, default: 20)
- `next_token` (optional): Pagination token

### 2. get_bedrock_prompt_details
Gets detailed information about a specific prompt.

**Parameters:**
- `prompt_identifier` (required): Prompt ID or ARN
- `prompt_version` (optional): Specific version (default: DRAFT)

### 3. invoke_bedrock_prompt
Invokes a prompt with variables and returns the model's response.

**Parameters:**
- `prompt_identifier` (required): Prompt ID or ARN
- `prompt_variables` (optional): Dict of variable substitutions
- `prompt_version` (optional): Specific version (default: DRAFT)

**Example variables:**
```json
{
  "question": "How do you feel about the economy?",
  "context": "Survey for small business owners"
}
```

### 4. list_bedrock_prompt_versions
Lists all versions of a specific prompt.

**Parameters:**
- `prompt_identifier` (required): Prompt ID or ARN
- `max_results` (optional): Number of results (1-100, default: 20)

### 5. invoke_bedrock_prompt_stream
Invokes a prompt with streaming response for real-time output.

**Parameters:**
- `prompt_identifier` (required): Prompt ID or ARN
- `prompt_variables` (optional): Dict of variable substitutions
- `prompt_version` (optional): Specific version (default: DRAFT)

**Returns:** Full completion text plus array of streamed chunks

### 6. batch_invoke_bedrock_prompt
Invokes a prompt multiple times with different variable sets in parallel.

**Parameters:**
- `prompt_identifier` (required): Prompt ID or ARN
- `variable_sets` (required): Array of variable dictionaries
- `prompt_version` (optional): Specific version (default: DRAFT)
- `max_workers` (optional): Parallel workers (1-10, default: 5)

**Example variable_sets:**
```json
[
  {"question": "How do you feel about the economy?"},
  {"question": "What are your hiring plans?"},
  {"question": "How do you view inflation?"}
]
```

**Returns:** Aggregated results with success/failure counts and individual responses

## Supported Model Types

The server automatically detects and formats requests for:

- **Anthropic Claude** (claude-3, claude-3-5-sonnet, etc.)
- **Amazon Titan** (titan-text-express, titan-text-lite)
- **Meta Llama** (llama-2, llama-3, etc.)
- **Mistral AI** (mistral-7b, mixtral-8x7b)
- **Cohere** (command, command-light)
- **AI21 Labs** (jurassic-2)

Each model type uses the appropriate request/response format automatically.

## Troubleshooting

### Server won't start
- Check that AWS credentials are configured: `aws sts get-caller-identity`
- Verify Python version: `python --version` (should be 3.10+)
- Check logs in Claude Desktop: Help → Show Logs

### "No credentials found" error
- Run `aws configure` to set up credentials
- Or use environment variables in the config file

### Prompt invocation fails
- Verify the prompt exists: List prompts first
- Check that the model specified in the prompt is available in your region
- Ensure you have permissions to invoke Bedrock models

### Variable substitution not working
- Check that variable names match exactly (case-sensitive)
- The server supports both `{{variable}}` and `{variable}` syntax
- View prompt details to see expected variable names

## Development

### Running Tests
```bash
# Test AWS connectivity
python bedrock_prompts_mcp_server.py
```

### Adding New Features
The server is structured to make it easy to add new Bedrock operations:
1. Add a new function in the main file
2. Register it in `list_tools()`
3. Handle it in `call_tool()`

## Security Notes

- Never commit AWS credentials to version control
- Use IAM roles when possible (e.g., on EC2 instances)
- Follow least-privilege principles for IAM permissions
- The server runs locally and doesn't expose network endpoints

## Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:ListPrompts",
        "bedrock:GetPrompt",
        "bedrock:ListPromptVersions",
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

## License

MIT

## Support

For issues or questions:
- Check the troubleshooting section
- Review AWS Bedrock documentation
- Check MCP documentation at https://modelcontextprotocol.io
