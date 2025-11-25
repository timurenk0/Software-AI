PROMPT_COMMIT = """
You are an expert software engineer writing perfect git commit messages and branch names.

Given the following git diff, perform two tasks:

1. Suggest a short, kebab-case branch name (max 40 chars). Examples:
    - feature/add-user-auth
    - bugfix/login-race-condition
    - refactor/extract-service-layer

2. Write a Conventional Commits message[](https://www.conventionalcommits.org):
    - type(scope): short summary (50 chars max)
    - blank line
    - detailed description if needed
    - bullet points for important changes

Type to use: feat, fix, refactor, chore, docs, test, perf, ci, build, style

Diff:
{diff}

Respond in JSON only:
{{
    "branch_name": "string",
    "commit_message": "string"
}}
"""
