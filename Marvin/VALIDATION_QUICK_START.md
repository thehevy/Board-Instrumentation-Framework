# Marvin Configuration Validator - Quick Start

**30-Second Start Guide**

## Run Validation

```bash
# Windows
validate_config.bat YourConfig.xml

# Linux/Mac
./validate_config.sh YourConfig.xml

# Any platform
python validate_config.py YourConfig.xml
```

## Common Commands

```bash
# Basic validation
validate_config.bat Application.xml

# Detailed output (shows all files, grid options)
validate_config.bat --verbose Application.xml

# Analyze alias cascading and dependencies
validate_config.bat --alias-cascade Application.xml

# Full diagnostic (everything)
validate_config.bat -v -a Application.xml
```

## What It Checks

✅ File encoding (UTF-8 BOM warnings)  
✅ XML syntax and structure  
✅ Tab ID references match definitions  
✅ Alias definitions and cascading  
✅ DynamicGrid file references  
✅ External file imports  
✅ Widget source files exist  

## Exit Codes

- `0` = ✅ Passed (warnings OK)
- `1` = ❌ Failed (errors found)

## Quick Fixes

### UTF-8 BOM Warning
```powershell
# Remove BOM
$content = Get-Content config.xml -Raw
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("config.xml", $content, $utf8)
```

### Missing Tab Definition
```xml
<!-- Add outside <Application> -->
<Tab ID="YourTabID">
  <Grid>...</Grid>
</Tab>
```

### Circular Alias
Break the chain by using direct values or restructuring.

## Integration

### Before Build
```gradle
// build.gradle
build.dependsOn validateConfig
```

### Before Launch
```batch
validate_config.bat config.xml && java -jar BIFF.Marvin.jar -i config.xml
```

### Pre-Commit
```bash
# .git/hooks/pre-commit
cd Marvin && python validate_config.py Application.xml
```

## More Info

See **VALIDATOR_README.md** for complete documentation.

---

**Phase 0 Complete** | February 2026 | Zero Dependencies | Cross-Platform
