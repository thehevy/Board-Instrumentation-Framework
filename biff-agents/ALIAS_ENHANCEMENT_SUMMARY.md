# Alias Support Enhancement Summary

## Overview
Enhanced both Minion and Marvin generators to use BIFF's alias system for improved user experience, following best practices from production configurations like Vision-SUT-actors.xml and E830 demo.

## Minion Configuration (MinionConfig.xml)

### Before:
```xml
<?xml version="1.0" ?>
<Minion SingleThreading="false">
  <Namespace>
    <Name>QuickStart</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="cpu.value">
      <Executable>D:\BIFF\Minion\Collectors\CPU.py</Executable>
      ...
```

### After:
```xml
<?xml version="1.0" ?>
<Minion SingleThreading="false">
  <AliasList>
    <!-- Configuration Aliases - Modify these values to customize your setup -->
    <Alias MinionNamespace="TestNamespace"/>
    <Alias OscarIP="192.168.1.100"/>
    <Alias OscarPort="1100"/>
    <Alias DefaultFrequency="1000"/>
    <Alias FastFrequency="500"/>
    <Alias SlowFrequency="2000"/>
  </AliasList>
  <Namespace>
    <Name>$(MinionNamespace)</Name>
    <DefaultFrequency>$(DefaultFrequency)</DefaultFrequency>
    <TargetConnection IP="$(OscarIP)" PORT="$(OscarPort)"/>
    ...
```

## Marvin Configuration

### New Structure:
```
Configs/
  ├── Application.xml        (imports DefinitionFiles/Aliases.xml)
  ├── Tab.QuickStart.xml     (uses aliases)
  ├── Grid.QuickStart.xml    (uses aliases)
  └── DefinitionFiles/
      └── Aliases.xml        (centralized alias definitions)
```

### DefinitionFiles/Aliases.xml:
```xml
<?xml version="1.0" ?>
<AliasList>
  <!-- Configuration Aliases - Modify these values to customize your dashboard -->
  
  <!-- Namespace Configuration -->
  <Alias MinionNamespace="TestNamespace"/>
  
  <!-- Network Configuration -->
  <Alias MarvinPort="52001"/>
  <Alias OscarIP="192.168.1.100"/>
  <Alias OscarPort="1100"/>
  
  <!-- Window Dimensions -->
  <Alias WindowWidth="1920"/>
  <Alias WindowHeight="1050"/>
  
  <!-- Layout Configuration -->
  <Alias Padding="5"/>
  <Alias GridHGap="5"/>
  <Alias GridVGap="5"/>
  <Alias HeartbeatRate="10"/>
  
  <!-- Widget Dimensions -->
  <Alias WidgetHeight="300"/>
  <Alias WidgetWidth="400"/>
  
  <!-- Color Palette - Customize widget colors -->
  <Alias ColorPrimary="#2196F3"/>
  <Alias ColorSuccess="#4CAF50"/>
  <Alias ColorWarning="#FF9800"/>
  <Alias ColorDanger="#F44336"/>
</AliasList>
```

### Application.xml (excerpt):
```xml
<Marvin>
  <AliasList>
    <!-- Import alias definitions from DefinitionFiles folder -->
    <Import>DefinitionFiles/Aliases.xml</Import>
  </AliasList>
  <Application Scale="auto">
    <CreationSize Width="$(WindowWidth)" Height="$(WindowHeight)"/>
    <Network Port="$(MarvinPort)"/>
    <Title>BIFF Quick Start - $(MinionNamespace)</Title>
    <Padding top="$(Padding)" bottom="$(Padding)" right="$(Padding)" left="$(Padding)"/>
    ...
```

### Grid.QuickStart.xml (excerpt):
```xml
<MarvinExternalFile>
  <Grid Align="N" hgap="10" vgap="10">
    <Widget row="1" column="1" Height="$(WidgetHeight)" Width="$(WidgetWidth)" ...>
      <Title>CPU Usage</Title>
      <MinionSrc Namespace="$(MinionNamespace)" ID="cpu.value"/>
    </Widget>
  </Grid>
</MarvinExternalFile>
```

## Benefits

1. **Easy Customization**: Change window size, widget dimensions, or colors in one place
2. **Better Maintainability**: No scattered magic numbers throughout configs
3. **Professional Structure**: Matches production BIFF deployments
4. **Deployment Flexibility**: Switch between dev/staging/prod by swapping alias files
5. **Consistent Naming**: Shared aliases between Minion and Marvin (MinionNamespace, OscarIP, etc.)
6. **Documentation**: Comments organize aliases by purpose

## Testing
Generated test configs show proper alias usage:
```
test-alias-output/
  ├── MinionConfig.xml
  ├── Application.xml
  ├── Tab.QuickStart.xml
  ├── Grid.QuickStart.xml
  └── DefinitionFiles/
      └── Aliases.xml
```

All configs successfully reference aliases using $(AliasName) syntax.
