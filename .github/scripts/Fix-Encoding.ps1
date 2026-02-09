# Markdown Encoding Fix Utility (PowerShell)
# Fix common UTF-8 encoding issues in markdown files

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    [switch]$All
)

Write-Host "Markdown Encoding Fix Utility" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

function Fix-MarkdownEncoding {
    param([string]$FilePath)
    
    Write-Host "Processing: $FilePath" -ForegroundColor Yellow
    
    # Create backup
    $backupPath = "$FilePath.bak"
    Copy-Item $FilePath $backupPath -Force
    
    # Read content
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $originalContent = $content
    
    # Fix common UTF-8 encoding issues
    # Em-dash (—)
    $content = $content -replace [char]0xE2 + [char]0x80 + [char]0x94, '--'
    
    # En-dash (–)
    $content = $content -replace [char]0xE2 + [char]0x80 + [char]0x93, '-'
    
    # Left single quote (')
    $content = $content -replace [char]0xE2 + [char]0x80 + [char]0x98, ''''
    
    # Right single quote (')
    $content = $content -replace [char]0xE2 + [char]0x80 + [char]0x99, ''''
    
    # Left double quote (")
    $content = $content -replace [char]0xE2 + [char]0x80 + [char]0x9C, '"'
    
    # Right double quote (")
    $content = $content -replace [char]0xE2 + [char]0x80 + [char]0x9D, '"'
    
    # Copyright symbol (©)
    $content = $content -replace [char]0xC2 + [char]0xA9, '©'
    
    # Registered trademark (®)
    $content = $content -replace [char]0xC2 + [char]0xAE, '®'
    
    # Trademark (™)
    $content = $content -replace [char]0xE2 + [char]0x84 + [char]0xA2, '™'
    
    # Ellipsis (…)
    $content = $content -replace [char]0xE2 + [char]0x80 + [char]0xA6, '...'
    
    # Non-breaking space
    $content = $content -replace [char]0xC2 + [char]0xA0, ' '
    
    # Remove replacement character
    $content = $content -replace [char]0xEF + [char]0xBF + [char]0xBD, ''
    
    # Remove trailing whitespace from each line
    $content = ($content -split "`n") | ForEach-Object { $_ -replace '\s+$', '' } | Join-String -Separator "`n"
    
    # Save fixed content
    Set-Content $FilePath -Value $content -Encoding UTF8 -NoNewline
    
    # Check if changes were made
    if ($content -eq $originalContent) {
        Write-Host "  ✓ No changes needed" -ForegroundColor Green
        Remove-Item $backupPath
    } else {
        Write-Host "  ✓ Fixed encoding issues" -ForegroundColor Green
        Write-Host "  Backup saved: $backupPath" -ForegroundColor Gray
    }
}

if ($All) {
    Write-Host "Fixing all markdown files in repository..." -ForegroundColor Cyan
    Write-Host ""
    
    $files = Get-ChildItem -Path $Path -Filter "*.md" -Recurse -File | 
        Where-Object { $_.FullName -notmatch '(node_modules|\.git|build)' }
    
    $count = 0
    foreach ($file in $files) {
        Fix-MarkdownEncoding -FilePath $file.FullName
        $count++
    }
    
    Write-Host ""
    Write-Host "Processed $count files" -ForegroundColor Green
} else {
    if (-not (Test-Path $Path)) {
        Write-Host "Error: File not found: $Path" -ForegroundColor Red
        exit 1
    }
    
    Fix-MarkdownEncoding -FilePath $Path
}

Write-Host ""
Write-Host "Done! Review changes and commit if satisfied." -ForegroundColor Cyan
Write-Host "To restore a backup: Move-Item file.md.bak file.md -Force" -ForegroundColor Gray
