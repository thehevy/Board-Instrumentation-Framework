# Agent Specifications

This directory contains specifications and configurations for GitHub Copilot agents and automated workflows for the BIFF project.

## Markdown Quality Management

### Quick Start

**Fix encoding issues in a file:**
```powershell
# Windows PowerShell
.\.github\scripts\Fix-Encoding.ps1 -Path "BIFF_User_Guide.md"

# Linux/Mac
./.github/scripts/fix-encoding.sh BIFF_User_Guide.md
```

**Fix all markdown files:**
```powershell
# Windows
.\.github\scripts\Fix-Encoding.ps1 -Path "." -All

# Linux/Mac
./.github/scripts/fix-encoding.sh --all
```

**Check markdown quality:**
```bash
# Install markdownlint-cli globally
npm install -g markdownlint-cli

# Run checks
markdownlint --config .github/agent-specs/.markdownlint.json **/*.md
```

### Files

#### Agent Specifications
- **markdown-quality-agent.md** - Comprehensive guide for maintaining markdown quality
  - Character encoding fixes
  - Line length management
  - Whitespace handling
  - Quality metrics and workflows

#### Configuration Files
- **.markdownlint.json** - Markdown linting rules
  - Line length: 120 characters
  - Trailing spaces: Not allowed
  - Inline HTML: Allowed (for XML examples)
  - Duplicate headings: Allowed for siblings

- **.markdown-link-check.json** - Link validation configuration
  - Timeout and retry settings
  - Pattern exclusions for local URLs
  - Status code handling

#### Scripts
- **Fix-Encoding.ps1** - PowerShell script for Windows encoding fixes
- **fix-encoding.sh** - Bash script for Linux/Mac encoding fixes

### Workflows

#### GitHub Actions
Located in `.github/workflows/markdown-quality.yml`:

- **Markdown Lint** - Runs on PR and push to master
- **Encoding Check** - Detects UTF-8 corruption
- **Trailing Whitespace** - Enforces clean line endings
- **Line Length** - Reports lines >120 characters
- **Link Validation** - Checks for broken links

### Quality Standards

#### Critical (Must Fix)
- ✅ No UTF-8 character corruption
- ✅ No trailing whitespace
- ✅ Lines under 120 characters (prose)

#### Important (Should Fix)
- Line length violations 120-200 chars
- Inconsistent formatting
- Broken internal links

#### Acceptable (Document)
- MD033: Inline HTML for XML examples
- MD024: Duplicate headings in reference docs
- MD001: Heading level jumps for hierarchy

### Common Issues and Fixes

#### Character Encoding
**Problem:** Smart quotes appear as `â€™` or `â€œ`

**Fix:**
```powershell
# Automatic
.\.github\scripts\Fix-Encoding.ps1 -Path "file.md"

# Manual PowerShell
$content = Get-Content "file.md" -Raw -Encoding UTF8
$content = $content -replace 'â€™', "'"
$content = $content -replace 'â€œ', '"'
Set-Content "file.md" -Value $content -Encoding UTF8
```

#### Trailing Whitespace
**Problem:** Spaces at end of lines

**Fix:**
```powershell
# PowerShell
(Get-Content "file.md") | ForEach-Object { $_ -replace '\s+$', '' } | 
  Set-Content "file.md" -Encoding UTF8

# Bash
sed -i 's/[[:space:]]*$//' file.md
```

#### Long Lines
**Problem:** Lines exceed 120 characters

**Fix:**
```markdown
# Before (150 chars)
This is a very long line that exceeds the 120 character limit and should be wrapped at a natural boundary such as a period, comma or space.

# After (properly wrapped)
This is a very long line that exceeds the 120 character limit and should be wrapped at a natural boundary
such as a period, comma or space.
```

### Integration

#### Pre-Commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check markdown quality before commit
markdownlint --config .github/agent-specs/.markdownlint.json \
  $(git diff --cached --name-only --diff-filter=ACM | grep '\.md$')
```

#### VS Code Integration
Add to `.vscode/settings.json`:
```json
{
  "markdownlint.config": {
    ".github/agent-specs/.markdownlint.json": true
  },
  "files.trimTrailingWhitespace": true,
  "editor.rulers": [120]
}
```

### Maintenance

**Monthly Tasks:**
- Review new markdownlint rules
- Update encoding patterns for new issues
- Check GitHub Actions workflow success rates

**Quarterly Tasks:**
- Update dependencies (markdownlint-cli, actions)
- Review and refine quality metrics
- Document new patterns or edge cases

### Support

For questions or improvements:
1. Review [markdown-quality-agent.md](markdown-quality-agent.md)
2. Check GitHub Actions run results
3. Open an issue with `documentation` label
4. Propose changes via pull request

### Resources

- [markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Markdown Spec](https://github.github.com/gfm/)
- [UTF-8 Encoding Reference](https://en.wikipedia.org/wiki/UTF-8)
