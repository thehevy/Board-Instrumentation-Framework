# Timer.py Usage Guide

**WARNING**: Timer.py requires complex state management and is not recommended for simple use cases.

## Issue

The Timer collector uses class-based state management that requires specific initialization sequences. Simple configurations will fail with:

```
Timer {timer_id} does not exist
```

## How Timer.py Works

Timer.py maintains an internal dictionary of `TimerInfo` objects. Each timer must be:
1. Created (with `create` or `create_and_start` action)
2. Managed through specific action sequences
3. Queried with exact timer ID matching

## Actions Available

- `get` - Get elapsed time (timer must already exist)
- `create` - Create timer but don't start
- `create_and_start` - Create and start immediately
- `get_auto_create` - Create, start, and get in one call
- `stop` - Stop timer
- `start` - Start or resume timer
- `pause` - Pause timer (start resumes)

## Attempted Configuration (FAILS)

```xml
<Collector ID="timer.value" Frequency="1000">
  <Executable>Collectors/Timer.py</Executable>
  <Param>Timer</Param>
  <Param>default</Param>
  <Param>get_auto_create</Param>
</Collector>
```

**Result**: Runtime error - timer state not properly managed across collector invocations.

## Alternatives

For simple incrementing values or time tracking, use:

### Option 1: RandomVal with StepValue
```xml
<Collector ID="counter" Frequency="1000">
  <Executable>Collectors/RandomVal.py</Executable>
  <Param>StepValue</Param>
  <Param>counter1</Param>
  <Param>0</Param>
  <Param>100</Param>
  <Param>1</Param>
</Collector>
```

### Option 2: Simple timestamp script
Create `Collectors/SimpleTimer.py`:
```python
#!/usr/bin/env python3
import time

def GetTimestamp():
    return int(time.time() * 1000)

if __name__ == '__main__':
    print(GetTimestamp())
```

```xml
<Collector ID="timestamp" Frequency="1000">
  <Executable>Collectors/SimpleTimer.py</Executable>
  <Param>GetTimestamp</Param>
</Collector>
```

## Recommendation

**Do not use Timer.py** unless you:
1. Fully understand its state management model
2. Have production requirements that need persistent timer tracking
3. Are willing to debug complex state initialization issues

For quickstart and testing scenarios, use RandomVal or CPU collectors instead.

## Production Use

If you must use Timer.py in production:
1. Study the Timer.py source code thoroughly
2. Create test configurations to understand action sequences
3. Add extensive error handling
4. Consider wrapping it in a custom script with proper state management
5. Document your exact usage pattern for future maintenance
