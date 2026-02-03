# Python 3.12+ Compatibility Fixes

**Date**: February 2, 2026  
**Status**: ✅ FIXED

## Issues Fixed

### 1. ✅ Removed Deprecated `imp` Module
**File**: `Minion/Helpers/DynamicPython.py` (Line 30)  
**Issue**: `import imp` - removed in Python 3.12  
**Fix**: Removed unused import (module was never used)

### 2. ✅ Fixed Invalid Escape Sequence
**File**: `Minion/Minion.py` (Line 57)  
**Issue**: `cursors=('/-\|')` - invalid escape sequence  
**Fix**: Changed to `cursors=(r'/-\|')` (raw string)

### 3. ✅ Added Shebangs to Collector Scripts
**Files**: 
- `Minion/Collectors/RandomVal.py`
- `Minion/Collectors/CPU.py`  
- `Minion/Collectors/Timer.py`

**Added**: `#!/usr/bin/env python3` for standalone execution

### 4. ✅ Fixed Incorrect Function Names in Generators
**File**: `biff-agents/biff_agents_core/generators/minion_generator.py`

**Changes**:
- CPU: `GetUsage` → `GetCPU_Percentage` (correct function name)
- RandomVal: Added `GetBoundedRandomValue` as first parameter
- Timer: Added `Timer` as function name parameter
- Removed: Invalid Memory and Storage templates (functions don't exist)

### 5. ✅ Fixed Quickstart Configuration
**File**: `biff-agents/quickstart_configs/MinionConfig.xml`

**Changes**:
```xml
<!-- BEFORE (BROKEN) -->
<Collector ID="randomval.value">
  <Executable>Collectors/RandomVal.py</Executable>
  <Param>0</Param>
  <Param>100</Param>
</Collector>

<!-- AFTER (FIXED) -->
<Collector ID="randomval.value">
  <Executable>Collectors/RandomVal.py</Executable>
  <Param>GetBoundedRandomValue</Param>
  <Param>0</Param>
  <Param>100</Param>
</Collector>
```

## Testing Checklist

- [ ] Minion starts on Python 3.12+
- [ ] RandomVal collector works
- [ ] CPU collector works
- [ ] Timer collector works
- [ ] Generated configs use correct function names
- [ ] No UTF-8 BOM in Python files (run: `file Minion/Collectors/*.py`)
- [ ] Execute permissions set (run: `chmod +x Minion/Collectors/*.py`)

## Remaining Manual Tasks

### BOM Removal (Linux/Mac)
```bash
cd Minion/Collectors
sed -i '1s/^\xEF\xBB\xBF//' *.py
```

### Execute Permissions (Linux/Mac)
```bash
chmod +x Minion/Collectors/*.py
```

### Verify No BOM
```bash
file Minion/Collectors/*.py | grep BOM
# Should return nothing if BOMs are removed
```

## Files Modified

1. `Minion/Helpers/DynamicPython.py` - Removed imp import
2. `Minion/Minion.py` - Fixed escape sequence
3. `Minion/Collectors/RandomVal.py` - Added shebang
4. `Minion/Collectors/CPU.py` - Added shebang
5. `Minion/Collectors/Timer.py` - Added shebang
6. `biff-agents/biff_agents_core/generators/minion_generator.py` - Fixed function names
7. `biff-agents/quickstart_configs/MinionConfig.xml` - Fixed function references

## Verification Commands

```bash
# Test Python 3.12 compatibility
python3.12 -c "import sys; print(f'Python {sys.version}')"

# Test Minion starts
cd Minion
python3.12 Minion.py -c ../Build/MinionConfig.xml -v

# Check for syntax warnings
python3.12 -Wall Minion.py -h

# Verify no import errors
python3.12 -c "import sys; sys.path.insert(0, 'Helpers'); import DynamicPython"
```

## Correct Collector Function References

### RandomVal.py Functions
- `GetBoundedRandomValue(min, max)` - Random value in range
- `GetBoundedRandomList(min, max, listSize)` - List of random values
- `GetScaledBoundedRandomValue(min, max, scale)` - Scaled random value
- `StepValue(id, start, stop, step)` - Stepped value sequence

### CPU.py Functions
- `GetCPU_Percentage()` - Overall CPU usage
- `GetCPU_Core_Percentage(which)` - Specific core usage
- `GetCPU_Core_PercentageList(startCore, count)` - Multiple cores

### Timer.py Functions
- `Timer(ID, Action)` - Timer operations
  - Actions: `get`, `create`, `create_and_start`, `get_auto_create`, `stop`, `start`, `pause`

## Configuration Example

```xml
<Minion SingleThreading="false">
  <Namespace>
    <Name>Production</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    
    <!-- RandomVal - Correct -->
    <Collector ID="random" Frequency="500">
      <Executable>Collectors/RandomVal.py</Executable>
      <Param>GetBoundedRandomValue</Param>
      <Param>0</Param>
      <Param>100</Param>
    </Collector>
    
    <!-- CPU - Correct -->
    <Collector ID="cpu" Frequency="1000">
      <Executable>Collectors/CPU.py</Executable>
      <Param>GetCPU_Percentage</Param>
    </Collector>
    
    <!-- Timer - Correct -->
    <Collector ID="timer" Frequency="100">
      <Executable>Collectors/Timer.py</Executable>
      <Param>Timer</Param>
      <Param>timer1</Param>
      <Param>get_auto_create</Param>
    </Collector>
  </Namespace>
</Minion>
```
