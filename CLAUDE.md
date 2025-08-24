# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains schema definitions and documentation for industrial machine identification types. The project defines standardized data structures for identifying and cataloging industrial machines across different types (Printing Press, Laminator, Slitter, Bag Machine, Pump, Pumping Station, Tank). It includes both sample data generation and MQTT publishing capabilities for industrial IoT integration.

## File Structure

- `MachineIdentificationType-Schema.json`: JSON Schema defining the structure and validation rules for machine identification data
- `MachineIdentificationType-Description.json`: Human-readable descriptions and field explanations for each property in the schema
- `readme.md`: Lists the machine types and corresponding MQTT topic names
- `generate_sample_payloads.py`: Python script to generate realistic sample machine identification payloads
- `publish_machineid.py`: Python script to publish machine identification payloads to MQTT brokers using configuration files
- `publish_config.json`: Configuration file for MQTT broker connection and machine topic mappings
- `machines/`: Directory containing individual sample payload files for each machine type
  - `press.json`: Sample payload for Printing Press
  - `lam.json`: Sample payload for Laminator
  - `slit.json`: Sample payload for Slitter
  - `bag.json`: Sample payload for Bag Machine
  - `pump.json`: Sample payload for Pump
  - `pumping_station.json`: Sample payload for Pumping Station
  - `tank.json`: Sample payload for Tank

## Schema Architecture

The core data structure is `MachineIdentificationType`, which contains comprehensive machine metadata including:

- **Identity fields**: AssetId, SerialNumber, ProductCode
- **Manufacturing details**: Manufacturer, Model, YearOfConstruction, Location
- **Technical specifications**: DeviceClass, HardwareRevision, SoftwareRevision
- **Operational data**: InitialOperationDate, DeviceManual
- **Integration points**: DefaultInstanceBrowseName (for MQTT topics), ProductInstanceUri

Required fields are strictly defined in the schema. The schema follows JSON Schema Draft 07 specification.

## Sample Data Generation

To generate new sample payloads:

```bash
# Generate all machine types and save to files
python3 generate_sample_payloads.py

# Generate specific machine type (prints to console)
python3 generate_sample_payloads.py press
python3 generate_sample_payloads.py lam
python3 generate_sample_payloads.py slit
python3 generate_sample_payloads.py bag
python3 generate_sample_payloads.py pump
python3 generate_sample_payloads.py pumping_station
python3 generate_sample_payloads.py tank

# Generate multiple payloads of specific type
python3 generate_sample_payloads.py press 3    # 3 printing press payloads
python3 generate_sample_payloads.py pump 5     # 5 pump payloads
```

This script:
- Creates realistic sample data for all 7 machine types
- Uses real industrial equipment manufacturer names and URIs
- Generates appropriate construction/operation date constraints
- Outputs individual files (`machines/*.json`) when run without arguments
- Prints JSON to console when machine type is specified
- Supports generating multiple payloads with clear separation headers
- Accepts case-insensitive machine type arguments
- Includes all required schema fields with realistic values

## MQTT Publishing

To publish machine identification payloads to an MQTT broker:

```bash
# Install required dependency
pip3 install paho-mqtt

# Publish using default configuration (publish_config.json)
python3 publish_machineid.py

# Use custom configuration file
python3 publish_machineid.py my_config.json

# Test without actually publishing (dry-run mode)
python3 publish_machineid.py --dry-run

# Verbose output for debugging
python3 publish_machineid.py -v
```

### Configuration File Structure

The `publish_config.json` file contains:

- **MQTT Broker Settings**: Connection details including host, port, credentials, QoS, and retain settings
- **Machine Definitions**: List of machines to publish with their types and target MQTT topics
- **Global Settings**: Publish timeout, retry attempts, and retry delay for robust publishing

### Topic Wrapper Handling

The script automatically detects topics ending with `MachineIdentificationType` and removes the outer JSON wrapper when publishing. This ensures the published payload contains only the machine identification fields (AssetId, ComponentName, etc.) rather than the full nested structure.

Example:
- Topic: `factory/pump/pump-101/MachineIdentificationType` → Publishes inner content only
- Topic: `factory/pump/pump-101` → Publishes full payload with wrapper

## Development Notes

- This is both a data specification project and an MQTT publishing tool for industrial IoT integration
- The `generate_sample_payloads.py` script uses only Python standard library dependencies
- The `publish_machineid.py` script requires `paho-mqtt` for MQTT broker communication
- Changes should maintain backward compatibility with existing industrial systems
- MQTT topic mapping follows the pattern: Press → Printing Press, Lam → Laminator, etc.
- Configuration-driven architecture allows easy customization for different industrial environments
- Supports both direct JSON file generation and real-time MQTT publishing workflows