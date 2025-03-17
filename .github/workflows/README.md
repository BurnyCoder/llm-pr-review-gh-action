# PR Diff Analysis with LLM

This GitHub Action automatically analyzes pull request diffs using a Large Language Model (LLM) via Portkey and provides feedback as a comment on the PR.

## What it does

When a pull request is opened, updated, or reopened, this workflow:

1. Checks out the repository
2. Gets the diff between the base branch and the PR branch
3. Gathers the entire codebase content for context
4. Sends both the diff and codebase to Gemini 2 Flash Thinking via Portkey
5. Posts the analysis as a comment on the PR

The analysis includes:
- Summary of changes
- Potential issues or bugs
- Suggestions for improvements
- Security concerns
- Code quality observations
- How the changes fit into the existing codebase

## Performance Optimizations

The workflow includes caching for Python dependencies, which significantly improves execution speed for subsequent runs by:
- Storing pip packages in the GitHub Actions cache
- Using a hash of your requirements.txt file as the cache key
- Reducing the need to repeatedly download the same packages

## Enhanced Context

This workflow is enhanced to include the entire codebase in the analysis. This provides the LLM with full context about your project, allowing it to:

- Understand the broader impact of changes
- Detect inconsistencies with existing code patterns
- Identify potential conflicts or integration issues
- Provide more relevant and insightful feedback

## Setup Requirements

To use this workflow, you need to add the following secrets to your GitHub repository:

1. `PORTKEY_API_KEY`: Your Portkey API key
2. `PORTKEY_VIRTUAL_KEY_GOOGLE`: Your Portkey virtual key for Google (Gemini)

### How to set up GitHub Secrets

1. Go to your repository on GitHub
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add the required secrets mentioned above

### Required Permissions

The workflow requires specific permissions to function correctly:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

These permissions allow the workflow to:
- Read repository contents
- Write comments to pull requests
- Add comments to issues

If you're using restrictive permissions in your repository settings, make sure these permissions are not further restricted.

## Customization

### Prompt Customization
You can customize the prompt in the `analyze-diff` job to change what kind of feedback the LLM provides.

### LLM Model Selection
The workflow currently uses Google's Gemini 2 Flash Thinking model, which is optimized for faster responses on code analysis tasks. You can modify the script to use other models available in the portkey.py module:

- `claude35sonnet` - Claude 3.5 Sonnet
- `claude37sonnet` - Claude 3.7 Sonnet
- `gpt4o` - GPT-4o
- `gemini2pro` - Gemini 2 Pro
- `o3minihigh` - o3-mini-high

Each model requires its corresponding virtual key environment variable.

### Branch Filtering
By default, this workflow runs for pull requests between any branches. If you want to limit it to specific target branches, you can uncomment and modify the `branches` section in the workflow file:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - develop
```

This will only run the workflow for PRs targeting the main or develop branches.

## Notes

- The workflow will use the full codebase and diff for analysis without any truncation
- You may need to adjust the Python version or dependencies based on your project's requirements 