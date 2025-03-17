# LLM PR Review GitHub Action

This GitHub Action automatically analyzes pull requests using an Gemini 2 Flash Thinking LLM (Large Language Model) and provides detailed feedback as a comment on the PR. The analysis includes a summary of changes, potential issues, suggestions for improvements, security concerns, and code quality observations.

## Features

- Automatically runs on PR creation and updates
- Analyzes code diff context-aware with the entire codebase
- Posts comprehensive analysis as a comment on the PR
- Uses Google's Gemini 2.0 Flash Thinking model via Portkey AI
- Caches Python dependencies for faster workflow runs

## Setup Instructions

Follow these steps to add this GitHub Action to your repository:

### 1. Create the Workflow File

Create the workflow file at `.github/workflows/analyze_pr_diff.yml` with the content from the template below.

```yaml
name: Analyze PR Diff with LLM

on:
  pull_request:
    types: [opened, synchronize, reopened]
    # Optional: Uncomment below to only run on PRs targeting specific branches
    # branches:
    #   - main
    #   - develop

# Add permissions needed to comment on PRs
permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  analyze-diff:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Cache Python dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Get PR diff
        id: get-diff
        run: |
          # Get the PR diff and save it to a file
          git diff ${{ github.event.pull_request.base.sha }} ${{ github.event.pull_request.head.sha }} > pr_diff.txt
          echo "diff_size=$(stat -c%s pr_diff.txt)" >> $GITHUB_OUTPUT
          
      - name: Create Python analysis script
        run: |
          cat > analyze_pr.py << 'EOFPY'
          import sys
          import os
          from portkey_ai import Portkey
          
          # Initialize Portkey client for Google
          portkey_google = Portkey(
              api_key=os.getenv("PORTKEY_API_KEY"),
              virtual_key=os.getenv("PORTKEY_VIRTUAL_KEY_GOOGLE")
          )
          
          # Inline the gemini2flashthinking function
          def gemini2flashthinking(prompt):
              """Wrapper function for Gemini 2 Flash Thinking"""
              completion = portkey_google.chat.completions.create(
                  messages=[{"role": "user", "content": prompt}],
                  model="gemini-2.0-flash-thinking-exp-01-21",
                  max_tokens=8192
              )
              return completion.choices[0].message.content
          
          # Import get_codebase directly from code2prompt package
          from code2prompt import get_codebase
          
          # Read the diff file
          with open('pr_diff.txt', 'r') as f:
              diff_content = f.read()
              
          # Get the entire codebase
          try:
              print("Gathering codebase content...")
              codebase_content = get_codebase(".")
              print("Codebase content gathered successfully.")
          except Exception as e:
              print(f"Error gathering codebase: {str(e)}")
              codebase_content = "Error: Could not retrieve codebase content."
          
          # Get environment variables for PR info
          github_repo = os.environ.get('GITHUB_REPOSITORY', 'Unknown repository')
          pr_number = os.environ.get('PR_NUMBER', 'Unknown PR')
          pr_title = os.environ.get('PR_TITLE', 'Unknown title')
          
          # Prepare prompt for the LLM
          prompt = f"""
          Please analyze the following Git diff from a pull request and provide feedback.
          You will be provided with both the diff and the entire codebase for context.
          
          Pull Request: {github_repo}/pull/{pr_number}
          Title: {pr_title}
          
          DIFF:
          ```
          {diff_content}
          ```
          
          CODEBASE:
          {codebase_content}
          
          Please provide:
          1. A summary of the changes
          2. Potential issues or bugs you notice
          3. Suggestions for improvements
          4. Any security concerns
          5. Code quality observations
          
          Consider how the changes fit into the existing codebase and if they maintain consistency with the existing code patterns.
          """
          
          # Send to LLM and get analysis
          print("Sending to LLM for analysis...")
          analysis = gemini2flashthinking(prompt)
          
          # Print the analysis
          print("\n--- LLM ANALYSIS OF PR DIFF ---\n")
          print(analysis)
          print("\n--- END OF ANALYSIS ---\n")
          
          # Save analysis to a file for GitHub comment creation
          with open('llm_analysis.md', 'w') as f:
              f.write(analysis)
          EOFPY
          
      - name: Analyze diff with LLM
        env:
          PORTKEY_API_KEY: ${{ secrets.PORTKEY_API_KEY }}
          PORTKEY_VIRTUAL_KEY_GOOGLE: ${{ secrets.PORTKEY_VIRTUAL_KEY_GOOGLE }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: python analyze_pr.py
          
      - name: Add LLM analysis as PR comment
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const analysis = fs.readFileSync('llm_analysis.md', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## LLM Analysis of PR Changes\n\n${analysis}`
            }) 
```

### 2. Create requirements.txt

Create a `requirements.txt` file in the root of your repository with the following dependencies:

```
portkey-ai>=1.0.0
code2prompt>=0.1.0
```

### 3. Set Up Portkey AI

1. Sign up for a [Portkey.ai](https://portkey.ai/) account if you don't already have one.
2. Create an API key in the Portkey dashboard.
3. Create a Virtual Key for Google in the Portkey dashboard, which will give you access to Gemini models.

### 4. Add GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `PORTKEY_API_KEY`: Your Portkey API key
   - `PORTKEY_VIRTUAL_KEY_GOOGLE`: Your Portkey Virtual Key for Google

### 5. Customize (Optional)

You can customize the workflow by:

- Modifying the prompt in the Python script to focus on specific aspects of code review
- Changing the trigger conditions (e.g., only run on specific branches)
- Adjusting the LLM model or parameters

## How It Works

1. When a PR is opened or updated, the workflow is triggered
2. The action checks out the code and installs dependencies
3. It generates a diff between the base and head of the PR
4. The Python script analyzes the diff with context from the codebase
5. The LLM generates an analysis of the changes
6. The analysis is posted as a comment on the PR

## Troubleshooting

- If the action fails to run, check the workflow logs for error messages
- Ensure your Portkey API keys are correctly set up as repository secrets
- Verify that the required Python packages are correctly listed in requirements.txt

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Todo

- Add support for Gemini API instead of just Portkey
- Move prompt to environment variable
- Support for more LLMs

## License

[MIT](LICENSE) 