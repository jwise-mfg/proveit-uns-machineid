# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains schema definitions and documentation for industrial machine identification types. The project defines standardized data structures for identifying and cataloging industrial machines across different types (Printing Press, Laminator, Slitter, Bag Machine).

## File Structure

- `MachineIdentificationType-Schema.json`: JSON Schema defining the structure and validation rules for machine identification data
- `MachineIdentificationType-Description.json`: Human-readable descriptions and field explanations for each property in the schema
- `readme.md`: Lists the machine types (Press, Lam, Slit, Bag) and corresponding MQTT topic names
- `generate_sample_payloads.py`: Python script to generate realistic sample machine identification payloads
- `machines/`: Directory containing individual sample payload files for each machine type
  - `press.json`: Sample payload for Printing Press
  - `lam.json`: Sample payload for Laminator
  - `slit.json`: Sample payload for Slitter
  - `bag.json`: Sample payload for Bag Machine

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

# Generate multiple payloads of specific type
python3 generate_sample_payloads.py press 3    # 3 printing press payloads
python3 generate_sample_payloads.py lam 5      # 5 laminator payloads
```

This script:
- Creates realistic sample data for all 4 machine types
- Uses real industrial equipment manufacturer names and URIs
- Generates appropriate construction/operation date constraints
- Outputs individual files (`machines/*.json`) when run without arguments
- Prints JSON to console when machine type is specified
- Supports generating multiple payloads with clear separation headers
- Accepts case-insensitive machine type arguments
- Includes all required schema fields with realistic values

## Development Notes

- This appears to be a data specification project rather than executable code
- No build, test, or deployment commands are present
- Changes should maintain backward compatibility with existing industrial systems
- MQTT topic mapping follows the pattern: Press → Printing Press, Lam → Laminator, etc.
- Sample data uses minimal dependencies (Python standard library only)