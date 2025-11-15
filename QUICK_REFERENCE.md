# Quick Reference Guide

## Common Use Cases

### 1. Generate Survey Responses at Scale

**Problem**: You need to simulate 100 survey responses with demographic variation.

**Solution**: Use batch invocation with different variable sets.

```python
# In Claude Desktop, just say:
"Batch invoke prompt survey-respondent with 100 different demographic profiles"

# The server will:
# 1. Run 100 parallel invocations (with max_workers=10)
# 2. Each with different variables like:
#    {"age": "35", "location": "TX", "income": "75000"}
#    {"age": "52", "location": "CA", "income": "120000"}
#    etc.
```

**Expected Output**:
```json
{
  "total_invocations": 100,
  "successful": 100,
  "failed": 0,
  "results": [...]
}
```

---

### 2. Test Multiple Questions on Same Persona

**Problem**: You have one persona prompt and want to test 10 different questions.

**Solution**: Use batch invocation with same persona, different questions.

```python
# In Claude Desktop:
"Batch invoke my-persona prompt with these 10 questions: [list questions]"

# Or programmatically:
variable_sets = [
    {"question": "How do you feel about the economy?"},
    {"question": "What are your hiring plans?"},
    {"question": "How do you view inflation?"},
    # ... 7 more
]
batch_invoke_prompt("PROMPT_ID", variable_sets, max_workers=5)
```

---

### 3. Generate Long-Form Content with Streaming

**Problem**: Your prompt generates a detailed report and you want to see progress.

**Solution**: Use streaming invocation.

```python
# In Claude Desktop:
"Stream the response from my-report-generator prompt"

# Returns chunks as they're generated:
{
  "completion": "Full text...",
  "chunks": ["Executive ", "Summary:\n", "The analysis...", ...],
  "chunk_count": 150
}
```

**Best for**:
- Long reports
- Detailed analysis
- Multi-paragraph responses
- When you want to show progress to users

---

### 4. A/B Test Different Prompt Versions

**Problem**: You have two versions of a prompt and want to compare outputs.

**Solution**: Use version management.

```python
# In Claude Desktop:
"Compare version 1 and version 2 of my-prompt with the same input"

# Programmatically:
result_v1 = invoke_prompt("PROMPT_ID", variables, prompt_version="1")
result_v2 = invoke_prompt("PROMPT_ID", variables, prompt_version="2")

# Compare:
print(f"V1: {result_v1['completion'][:100]}...")
print(f"V2: {result_v2['completion'][:100]}...")
```

---

### 5. Work with Multiple Model Types

**Problem**: You want to test the same prompt across different models.

**Solution**: The server automatically handles different model formats.

```python
# Create prompts with different models in Bedrock:
# - prompt-claude: Uses claude-3-5-sonnet
# - prompt-titan: Uses amazon.titan-text-express
# - prompt-llama: Uses meta.llama3-70b

# Invoke each:
claude_result = invoke_prompt("prompt-claude", variables)
titan_result = invoke_prompt("prompt-titan", variables)
llama_result = invoke_prompt("prompt-llama", variables)

# Server handles request/response formatting automatically
```

**Supported Models**:
- Claude (Anthropic)
- Titan (Amazon)
- Llama (Meta)
- Mistral AI
- Cohere
- AI21 Labs

---

### 6. Debug Prompt Templates

**Problem**: You're not sure what variables your prompt expects.

**Solution**: Get prompt details first.

```python
# In Claude Desktop:
"Show me the details and required variables for prompt VSWZVOISYG"

# Returns:
{
  "name": "survey-respondent",
  "template": "Answer this: {{question}}...",
  "inputVariables": [
    {"name": "question"}
  ]
}
```

---

### 7. Parallel Processing for Performance

**Problem**: You need to generate 50 responses quickly.

**Solution**: Use batch invocation with higher max_workers.

```python
# Default (5 workers) - ~10 seconds per batch of 5
batch_invoke_prompt("ID", variable_sets, max_workers=5)

# Faster (10 workers) - ~10 seconds per batch of 10
batch_invoke_prompt("ID", variable_sets, max_workers=10)

# Note: AWS has rate limits, so don't go too high
```

**Performance Tips**:
- max_workers=5: Good default, safe rate limits
- max_workers=10: Faster, watch for throttling
- Each invocation ~2-10 seconds depending on response length

---

### 8. Handle Errors Gracefully

**Problem**: Some invocations might fail due to throttling or validation.

**Solution**: Batch invocation tracks successes and failures separately.

```python
result = batch_invoke_prompt("ID", variable_sets)

print(f"Successful: {result['successful']}/{result['total_invocations']}")

# Check failures:
if result['failed'] > 0:
    for error in result['errors']:
        print(f"Failed: {error['variables']} - {error['error']}")

# Retry just the failed ones:
retry_sets = [e['variables'] for e in result['errors']]
retry_result = batch_invoke_prompt("ID", retry_sets)
```

---

## Performance Benchmarks

Based on typical usage:

| Operation | Time | Notes |
|-----------|------|-------|
| Single invoke | 2-5s | Depends on response length |
| Batch invoke (5) | 5-10s | Parallel, limited by slowest |
| Batch invoke (50) | 50-100s | 10 batches × max_workers=5 |
| Streaming | 2-10s | Same as regular, but shows progress |
| List prompts | <1s | Fast, cached |
| Get details | <1s | Fast, metadata only |

---

## Best Practices

### 1. Variable Naming
- Use descriptive names: `question`, `demographic_data`, `context`
- Match exactly (case-sensitive): `{{Question}}` ≠ `{{question}}`
- Both `{{var}}` and `{var}` syntax supported

### 2. Batch Size
- Small batches (5-10): Quick results, good for testing
- Medium batches (20-50): Production use
- Large batches (100+): Split into multiple calls

### 3. Error Handling
- Always check `result["success"]` 
- Batch results have separate `errors` array
- Implement retry logic for transient failures

### 4. Model Selection
- Claude: Best for complex reasoning, multi-turn
- Titan: Fast, cost-effective for simple tasks
- Llama: Open-source alternative
- Match model to task complexity

### 5. Streaming
- Use for responses >500 words
- Good UX for real-time display
- Slightly higher latency overhead
- Not all models support streaming equally

---

## Troubleshooting

### "No credentials found"
```bash
aws configure
# or
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
```

### "Throttling exception"
- Reduce max_workers from 10 → 5 → 3
- Add delays between batches
- Request limit increase from AWS

### "Variable not found in template"
- Check variable name spelling (case-sensitive)
- Get prompt details to see expected variables
- Use `{{var}}` or `{var}` syntax consistently

### "Model not supported in region"
- Check model availability: `aws bedrock list-foundation-models`
- Some models only in us-east-1, us-west-2
- Update model_id in prompt configuration

---

## Advanced: Custom Model Support

If you need to support a new model type:

1. Add to `get_model_type()` detection
2. Create `build_request_body_<model>()` function
3. Create `parse_response_<model>()` function
4. Add to `build_request_body()` and `parse_model_response()` mappings

Example for hypothetical "NewModel":

```python
def build_request_body_newmodel(filled_template, inference_config, additional_fields):
    return {
        "input": filled_template,
        "parameters": {
            "max_length": int(inference_config.get("maxTokens", 2000)),
            "temp": float(inference_config.get("temperature", 1.0))
        }
    }

def parse_response_newmodel(response_body):
    return response_body.get("output", {}).get("text", "")
```
