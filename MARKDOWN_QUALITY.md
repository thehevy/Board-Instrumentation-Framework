# Markdown Quality Validation

This repository uses the [markdown_quality_validator](https://github.com/thehevy/markdown_quality_validator) to ensure consistent documentation quality.

## Quick Start

### Validate Single File

```powershell
python markdown_validator.py README.md
```

### Validate All Markdown

```powershell
python markdown_validator.py .
```

### Auto-Fix Issues

```powershell
# Fix single file
python markdown_validator.py README.md --fix

# Fix all files
python markdown_validator.py . --fix
```

### Get Quality Score

```powershell
python markdown_validator.py README.md --score
# Output: Quality Score: 96/100
```

## Installation

### Prerequisites

Install Node.js from <https://nodejs.org/>, then install markdownlint-cli:

```powershell
npm install -g markdownlint-cli
```

Verify installation:

```powershell
markdownlint --version
```

### Optional: Pre-Commit Hook

To automatically validate markdown before each commit:

```powershell
.\setup-markdown-quality.ps1
```

This will reject commits with markdown quality issues. Bypass with:

```powershell
git commit --no-verify
```

## Configuration

Edit [.markdownlint.json](.markdownlint.json) to customize rules:

```json
{
  "MD013": { "line_length": 120 },
  "MD033": { "allowed_elements": ["details", "summary"] },
  "MD041": false
}
```

## Quality Scoring

- **100 points**: Perfect documentation
- **-2 points** per violation
- **Minimum**: 0 points

## Common Fixes

### Line Length (MD013)

Lines should be ≤120 characters (code blocks and tables excluded).

**Fix**: Break long lines or use auto-fix.

### No Inline HTML (MD033)

Only `<details>` and `<summary>` tags allowed.

**Fix**: Convert HTML to markdown syntax.

### First Line Must Be Heading (MD041)

Disabled in this repo for flexibility.

## VS Code Integration

Install the [markdownlint extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) for real-time validation:

1. Press `Ctrl+P`
2. Run: `ext install DavidAnson.vscode-markdownlint`
3. Restart VS Code

## CI/CD Integration

See `.github/workflows/` for GitHub Actions examples (if configured).

## Files

- `markdown_validator.py` - Standalone validator script
- `.markdownlint.json` - Rule configuration
- `setup-markdown-quality.ps1` - Pre-commit hook installer (PowerShell)

## Troubleshooting

### "markdownlint-cli not installed"

```powershell
npm install -g markdownlint-cli
```

### "npm not found"

Install Node.js from <https://nodejs.org/>

### Validation too strict

Edit `.markdownlint.json` to disable specific rules:

```json
{
  "MD013": false  // Disable line length check
}
```

## Documentation

- [Markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [Original Validator Repo](https://github.com/thehevy/markdown_quality_validator)
