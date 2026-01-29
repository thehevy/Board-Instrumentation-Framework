# Markdown Style Guide for BIFF Project

This project uses markdownlint to maintain consistent Markdown formatting. The `.markdownlint.json` configuration file defines our style rules.

## Enabled Rules

### Strict Rules (Always Enforced)

- **MD001** - Heading levels increment by one (h1 → h2 → h3, not h1 → h3)
- **MD022** - Headings must have blank lines above and below
- **MD032** - Lists must have blank lines before and after

### Relaxed Rules (Disabled for Project Style)

- **MD036** - Allow emphasis as headings (we use `**Bold Text**` for subheadings in code blocks)
- **MD040** - Allow fenced code blocks without language (we use plain blocks for diagrams/examples)
- **Line Length** - Disabled (no line length limits)
- **No Inline HTML** - Disabled (we use HTML when needed)

## Common Issues & Fixes

### Issue: MD040 - Fenced code blocks should have a language

**Before:**
````markdown
```
code here
```
````

**Fix Option 1** - Add language identifier:
````markdown
```text
diagram or plain text
```
````

**Fix Option 2** - Disable rule (already done in our config)

### Issue: MD036 - Emphasis used instead of heading

**Before:**
```markdown
```
**File Name**
```
```

**Fix Option 1** - Use proper heading:
```markdown
#### File Name

```text
content
```
```

**Fix Option 2** - Disable rule (already done in our config)

### Issue: MD032 - Lists should be surrounded by blank lines

**Before:**
```markdown
Some text here
- List item 1
- List item 2
Next paragraph
```

**Fix:**
```markdown
Some text here

- List item 1
- List item 2

Next paragraph
```

### Issue: MD022 - Headings should be surrounded by blank lines

**Before:**
```markdown
### Heading
Text immediately after
```

**Fix:**
```markdown
### Heading

Text with blank line
```

### Issue: MD001 - Heading levels increment by one

**Before:**
```markdown
## Section

#### Subsection (skipped h3)
```

**Fix:**
```markdown
## Section

### Subsection

#### Sub-subsection
```

## VS Code Integration

The `.markdownlint.json` file is automatically detected by the [markdownlint extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint).

### Recommended VS Code Settings

Add to your `.vscode/settings.json`:

```json
{
  "markdownlint.config": {
    "MD036": false,
    "MD040": false
  },
  "[markdown]": {
    "editor.formatOnSave": false,
    "editor.codeActionsOnSave": {
      "source.fixAll.markdownlint": true
    }
  }
}
```

## Pre-commit Hook (Optional)

To automatically check markdown on commit:

```bash
# Install markdownlint-cli
npm install -g markdownlint-cli

# Create .git/hooks/pre-commit
#!/bin/sh
markdownlint '**/*.md' --config .markdownlint.json
```

## CI/CD Integration (Future)

For GitHub Actions:

```yaml
- name: Lint Markdown
  uses: DavidAnson/markdownlint-cli2-action@v9
  with:
    globs: '**/*.md'
```

## Project-Specific Guidelines

### Code Examples in Documentation

When documenting code blocks with headers, use proper headings instead of emphasis:

**Preferred:**
```markdown
#### Example: Shell Command

```bash
command here
```
```

**Acceptable (if needed for layout):**
```markdown
```text
**Example: Shell Command**
command here
```
```

### Diagrams and ASCII Art

Use `text` language for plain diagrams:

````markdown
```text
Minion → Oscar → Marvin
```
````

### Long Lines

No line length restrictions - write naturally. Markdown renderers handle wrapping.

## Fixing Existing Files

To apply these rules to existing files:

```bash
# Auto-fix (use with caution)
markdownlint --fix '**/*.md'

# Check only
markdownlint '**/*.md'
```

## When to Update This Guide

- New team members join
- Markdownlint rule changes
- Community feedback on documentation style
- Integration with new tools (pre-commit, CI/CD)

---

**Last Updated:** January 29, 2026
**Maintainer:** BIFF Development Team
