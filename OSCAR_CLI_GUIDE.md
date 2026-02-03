# Oscar CLI Commands - Week 5 Day 2

## Quick Reference

### Generate Oscar Config from Minion

Generate a unified Oscar configuration from an existing Minion config:

```bash
biff oscar generate --from-minion MinionConfig.xml -o OscarConfig.xml
```

With multiple Marvin instances:

```bash
biff oscar generate --from-minion MinionConfig.xml --marvin-count 3 -o OscarConfig.xml
```

Per-namespace Oscar configs (separate Oscar for each namespace):

```bash
biff oscar generate --from-minion MinionConfig.xml --per-namespace -o Oscar
# Creates: Oscar_Namespace1.xml, Oscar_Namespace2.xml, etc.
```

### Validate Minion → Oscar Routing

Check that Minion target ports match Oscar incoming ports:

```bash
biff oscar validate --minion MinionConfig.xml --oscar OscarConfig.xml
```

Success output:
```
✓ Routing validation passed!
  Minion target ports match Oscar incoming ports
  Oscar has valid target connections
```

Error output:
```
✗ Found 2 routing error(s):
  1. Minion namespace 'Production' targets port 1100, but Oscar listens on port 1200
  2. Oscar has no TargetConnections (no Marvin instances configured)
```

### Analyze Minion Configuration

Get insights about your Minion setup:

```bash
biff oscar analyze --minion MinionConfig.xml
```

Output:
```
Configuration: MinionConfig.xml

Namespaces: 3
Total Collectors: 12
Total Actors: 2
Avg Collectors/Namespace: 4.0
Avg Actors/Namespace: 0.7

Target Connections:
  • localhost:1100
  • 192.168.1.50:1100

High-Frequency Collectors (<500ms):
  • System.cpu: 100ms
  • Network.bandwidth: 250ms
```

JSON output for scripting:

```bash
biff oscar analyze --minion MinionConfig.xml --json
```

### Generate Deployment Guide

Create a complete deployment guide with step-by-step instructions:

```bash
biff oscar deploy-guide --minion MinionConfig.xml -o DEPLOY.md
```

With existing Oscar config:

```bash
biff oscar deploy-guide --minion MinionConfig.xml --oscar OscarConfig.xml -o DEPLOY.md
```

## Example Workflow

1. **Start with a Minion config** you already have:
   ```bash
   biff oscar analyze --minion MinionConfig.xml
   ```

2. **Generate Oscar config automatically**:
   ```bash
   biff oscar generate --from-minion MinionConfig.xml --marvin-count 2 -o OscarConfig.xml
   ```

3. **Validate the routing**:
   ```bash
   biff oscar validate --minion MinionConfig.xml --oscar OscarConfig.xml
   ```

4. **Create deployment guide**:
   ```bash
   biff oscar deploy-guide --minion MinionConfig.xml --oscar OscarConfig.xml -o DEPLOY.md
   ```

5. **Deploy using the guide**:
   ```bash
   cat DEPLOY.md
   # Follow the instructions!
   ```

## Common Use Cases

### Multi-Marvin Setup

Deploy 3 Marvin instances load-balanced through Oscar:

```bash
biff oscar generate \
  --from-minion MinionConfig.xml \
  --marvin-count 3 \
  --oscar-id "ProductionOscar" \
  -o OscarConfig.xml
```

### Per-Namespace Isolation

Separate Oscar for each Minion namespace (isolated routing):

```bash
biff oscar generate \
  --from-minion MinionConfig.xml \
  --per-namespace \
  -o Oscar
```

### Pre-Deployment Validation

Before deploying to production, validate your configs:

```bash
# Check Minion config structure
biff oscar analyze --minion MinionConfig.xml

# Validate routing
biff oscar validate --minion MinionConfig.xml --oscar OscarConfig.xml

# Generate deployment guide
biff oscar deploy-guide --minion MinionConfig.xml --oscar OscarConfig.xml -o DEPLOY.md
```

## Benefits

- **No manual Oscar config editing**: Generate from existing Minion configs
- **Automatic port allocation**: Handles multiple Marvin instances automatically
- **Validation before deployment**: Catch configuration errors early
- **Deployment documentation**: Auto-generated step-by-step guides
- **Configuration insights**: Understand your Minion setup (collector counts, high-frequency collectors, etc.)
