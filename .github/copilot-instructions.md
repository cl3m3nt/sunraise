## Security Rules (Critical)

Always ensure that no secrets are introduced into the codebase.

- Never hardcode API keys, tokens, passwords, or private keys
- Always use environment variables or secret managers
- Never place secrets in logs, comments, or tests
- Treat any credential-like string as sensitive

If a secret is detected or suspected:
- warn explicitly
- suggest removal immediately
- propose secure alternatives


## Code Review Behavior

When reviewing or generating code:
- Actively scan for secrets, tokens, or embedded credentials
- Treat any string resembling a key, token, or password as sensitive
- Flag insecure patterns (e.g. "api_key = '...'")
- Recommend secure storage patterns by default


## PR Generation Behavior

When generating pull requests:
- Use a structured Markdown format
- Be concise and technical
- Focus on impact, changes, testing, and risks
- Avoid filler text