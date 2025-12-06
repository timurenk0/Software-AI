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
PROMPT_FILE_SELECTION="""
You are an exprt Python engineer.

Issue:
Title: {title}
Body:
{body}
Labels: {labels}

Available files:
{files_list}

Task: Return ONLY the files that need to be changed to fix this issue.
Max 8 files. If < 75 percent sure, return fewer or empty. 

Return valid JSON only:
{{
  "files": ["list", "of", "paths.py"],
  "confidence": 85,
  "reasoning": "short explanation"
}}
"""
PROMPT_RESOLVE="""
You are an expert GitHub issue resolver in Python.

Issue #{issue_number}: {title}
{body}

You must fix it by editing ONLY these files:

{files_with_content}

Return valid JSON with full new content for each file:

{{
  "files": {{
    "path/to/file.py": "full new file content",
    "path/to/file.py": "full new file content"
  }},
  "explanation": "What you changed and why"
}}
"""