# Markdown Quality Agent

## Purpose

This agent is responsible for maintaining markdown document quality across the BIFF project,
including user guides, README files, and documentation. It ensures consistent formatting,
proper encoding, and adherence to markdown best practices.

## Responsibilities

### 1. Character Encoding Management
- Fix UTF-8 encoding issues (smart quotes, em-dashes, copyright symbols)
- Convert corrupted character sequences to proper Unicode
- Ensure consistent encoding across all markdown files

### 2. Line Length Compliance
- Wrap prose lines to 120 characters maximum
- Preserve code blocks, tables, XML examples, and lists
- Break lines at natural boundaries (sentences, commas, phrases)
- Maintain readability while adhering to MD013 standard

### 3. Whitespace Management
- Remove trailing whitespace from all lines (MD009)
- Ensure consistent blank line usage
- Preserve intentional formatting in code blocks

### 4. Markdown Lint Compliance
- Address critical markdown lint errors
- Prioritize: MD009 (trailing spaces), MD013 (line length)
- Document acceptable warnings: MD033 (inline HTML for XML examples), MD024 (duplicate headings)

## Target Files

### Primary Documents
- `BIFF_User_Guide.md` - Main user and developer guide (4600+ lines)
- `BIFF_Cleaned.md` - Cleaned version of user guide
- `README.md` - Project overview and getting started

### Secondary Documents
- Agent specifications in `.github/agent-specs/*.md`
- Component READMEs in subdirectories
- Documentation in `Minion/`, `Oscar/`, `Marvin/` directories

## Configuration

The agent uses `.github/agent-specs/.markdownlint.json` for linting rules:

```json
{
  "MD013": { "line_length": 120, "tables": false, "code_blocks": false },
  "MD033": false,
  "MD024": { "siblings_only": true }
}
```

## Workflows

### Character Encoding Fix Workflow
```powershell
# Fix common UTF-8 issues
$content = Get-Content "file.md" -Raw -Encoding UTF8
$content = $content -replace [char]0xE2 + [char]0x80 + [char]0x93, '-'
$content = $content -replace [char]0xE2 + [char]0x80 + [char]0x94, '--'
$content = $content -replace [char]0xE2 + [char]0x80 + [char]0x98, ''''
$content = $content -replace [char]0xE2 + [char]0x80 + [char]0x99, ''''
$content = $content -replace [char]0xE2 + [char]0x80 + [char]0x9C, '"'
$content = $content -replace [char]0xE2 + [char]0x80 + [char]0x9D, '"'
$content = $content -replace [char]0xC2 + [char]0xA9, '©'
Set-Content "file.md" -Value $content -Encoding UTF8 -NoNewline
```

### Trailing Whitespace Removal
```powershell
(Get-Content "file.md") | ForEach-Object { $_ -replace '\s+$', '' } | 
  Set-Content "file.md" -Encoding UTF8
```

### Line Length Wrapping
```powershell
# Intelligent wrapping at sentence/phrase boundaries
# Preserve code blocks, tables, XML, lists
# Break at periods, commas, or spaces before 120 chars
# See implementation in agent logic
```

## Quality Checks

### Pre-Commit Validation
1. Run markdown lint: `markdownlint *.md`
2. Check character encoding: No UTF-8 corruption
3. Verify line lengths: Max 120 chars for prose
4. Validate trailing spaces: None allowed

### Error Priority
1. **Critical** (Must Fix)
   - Character encoding corruption
   - Trailing whitespace (MD009)
   - Excessively long lines (>200 chars)

2. **Important** (Should Fix)
   - Line length 120-200 chars (MD013)
   - Inconsistent formatting

3. **Acceptable** (Document)
   - MD033 (Inline HTML) - Required for XML examples
   - MD024 (Duplicate headings) - Common in reference docs
   - MD001 (Heading levels) - Document structure choice

## Usage Examples

### Fix All Critical Errors
```bash
# User request: "Fix only critical errors"
# Agent actions:
1. Fix character encoding (© → ©, "" → --, '' → ', etc.)
2. Remove trailing whitespace
3. Wrap lines >120 chars at natural boundaries
```

### Comprehensive Quality Pass
```bash
# User request: "Make file error-free"
# Agent actions:
1. Character encoding fixes
2. Trailing whitespace removal
3. Line wrapping to 120 chars
4. Document remaining acceptable warnings
```

### Bulk Processing
```bash
# Process multiple files
Get-ChildItem -Path "." -Filter "*.md" -Recurse | ForEach-Object {
    # Apply encoding fixes
    # Remove trailing spaces
    # Wrap long lines
    Write-Host "Processed: $($_.FullName)"
}
```

## Integration Points

### GitHub Actions
Future integration with `.github/workflows/markdown-quality.yml`:
- Run on PR creation/updates
- Check for encoding issues
- Validate line lengths
- Report quality metrics

### Pre-Commit Hooks
```bash
# .git/hooks/pre-commit
markdownlint -c .github/agent-specs/.markdownlint.json *.md
```

## Success Criteria

### Document Quality Metrics
- **Zero** character encoding errors
- **Zero** trailing whitespace violations
- **<5%** line length violations (>120 chars)
- All critical lint errors resolved

### Deliverables
- Clean, properly encoded markdown files
- Consistent formatting across documentation
- Readable diffs in version control
- Maintainable documentation structure

## Known Limitations

### Preserved Warnings
- **MD033**: XML/HTML tags in examples are intentional
- **MD024**: Duplicate headings ("Example", "Attributes") in reference docs
- **MD001**: Heading level jumps for visual hierarchy

### Edge Cases
- Very long URLs (cannot wrap)
- Code examples requiring specific line lengths
- ASCII art or diagrams
- Embedded data or configurations

## Maintenance

### Regular Reviews
- Monthly: Review new markdown lint rules
- Quarterly: Update character encoding patterns
- As-needed: Adjust line wrapping logic

### Tool Updates
- Monitor markdownlint updates
- Test new rules against existing docs
- Update .markdownlint.json configuration

## Contact

For questions or improvements to markdown quality processes:
- Update this agent specification
- Discuss in project documentation issues
- Propose changes via pull request
