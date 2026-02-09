#!/bin/bash
# Fix common UTF-8 encoding issues in markdown files

set -e

echo "Markdown Encoding Fix Utility"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if a file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <file.md>"
    echo "   or: $0 --all (to fix all markdown files)"
    exit 1
fi

fix_encoding() {
    local file=$1
    echo -e "${YELLOW}Processing: $file${NC}"
    
    # Create backup
    cp "$file" "$file.bak"
    
    # Fix common encoding issues
    # Em-dash (—)
    sed -i 's/â€"/--/g' "$file"
    
    # En-dash (–)  
    sed -i 's/â€"/-/g' "$file"
    
    # Left single quote (')
    sed -i "s/â€˜/'/g" "$file"
    
    # Right single quote (')
    sed -i "s/â€™/'/g" "$file"
    
    # Left double quote (")
    sed -i 's/â€œ/"/g' "$file"
    
    # Right double quote (")
    sed -i 's/â€/"/g' "$file"
    
    # Copyright symbol (©)
    sed -i 's/Â©/©/g' "$file"
    
    # Registered trademark (®)
    sed -i 's/Â®/®/g' "$file"
    
    # Trademark (™)
    sed -i 's/â„¢/™/g' "$file"
    
    # Non-breaking space
    sed -i 's/Â / /g' "$file"
    
    # Ellipsis (…)
    sed -i 's/â€¦/.../g' "$file"
    
    # Remove trailing whitespace
    sed -i 's/[[:space:]]*$//' "$file"
    
    # Check if changes were made
    if diff -q "$file" "$file.bak" > /dev/null; then
        echo -e "${GREEN}✓ No changes needed${NC}"
        rm "$file.bak"
    else
        echo -e "${GREEN}✓ Fixed encoding issues${NC}"
        echo "  Backup saved: $file.bak"
    fi
}

if [ "$1" == "--all" ]; then
    echo "Fixing all markdown files in repository..."
    echo ""
    
    count=0
    while IFS= read -r file; do
        fix_encoding "$file"
        count=$((count + 1))
    done < <(find . -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/build/*')
    
    echo ""
    echo -e "${GREEN}Processed $count files${NC}"
else
    if [ ! -f "$1" ]; then
        echo -e "${RED}Error: File not found: $1${NC}"
        exit 1
    fi
    
    fix_encoding "$1"
fi

echo ""
echo "Done! Review changes and commit if satisfied."
echo "To restore a backup: mv file.md.bak file.md"
