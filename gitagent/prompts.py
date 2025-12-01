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
PROMPT_REVIEW = """
You are a senior Python code reviewer with 15+ years of experience.

Review ONLY the modified files below for:
- Real bugs (wrong logic, exceptions, edge cases)
- Security issues
- Performance problems
- Anti-patterns
- Unused variables/imports
- Type mismatches
- Missing error handling

DO NOT flag:
- print() statements (may be intentional)
- TODO/FIXME (unless critical)
- Style issues (we have linters)

Modified files and their full content:

{files_content}

Diff:
{diff}

Respond in VALID JSON ONLY:
{{
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "file": "path/to/file.py",
      "description": "Clear explanation of the real problem"
    }}
  ],
  "summary": "All good" or "Found X potential issues"
}}
"""
PROMPT_RESOLVE = """
You are an autonomous senior developer fixing real GitHub issues of ones project repository.

Issue: #{issue_number}
Title: {issue_title}
Body: {issue_body}
Labels: {issue_labels}

Your job: Generate ONLY the correct code changes needed to fully resolve the issue.

Rules:
1. Return full file contents (not patches) for every file that must be changed
2. Do NOT explain - only return JSON
3. If no code change is needed, return empty "changes"
4. Be precide and production-ready


Respond in VALID JSON ONLY:
{{
  "changes": {{
    "path/to/file.py": "<full new file content>",
    "another/file.py": "<full new file content>",
  }}
}}
"""