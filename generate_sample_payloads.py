#!/usr/bin/env python3
"""
Generate sample machine identification payloads for each machine type.
Uses the MachineIdentificationType schema to create realistic sample data.
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta


def generate_construction_date():
    """Generate a construction date within the last 20 years."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=20*365)
    random_days = random.randint(0, (end_date - start_date).days)
    construction_date = start_date + timedelta(days=random_days)
    return construction_date


def generate_operation_date(construction_date):
    """Generate an operation date within the last 10 years, but after construction."""
    end_date = datetime.now()
    # Operation date must be after construction and within last 10 years
    earliest_operation = max(construction_date, end_date - timedelta(days=10*365))
    
    if earliest_operation >= end_date:
        earliest_operation = construction_date
    
    random_days = random.randint(0, (end_date - earliest_operation).days)
    operation_date = earliest_operation + timedelta(days=random_days)
    return operation_date


# Manufacturer data with matching names and URIs
manufacturers = {
    "heidelberg": {
        "name": "Heidelberger Druckmaschinen AG",
        "uri": "https://www.heidelberg.com"
    },
    "komori": {
        "name": "Komori Corporation",
        "uri": "https://www.komori.com"
    },
    "bobst": {
        "name": "BOBST Group SA",
        "uri": "https://www.bobst.com"
    },
    "atlas": {
        "name": "Atlas Converting Equipment Ltd.",
        "uri": "https://www.atlasconverting.com"
    },
    "comexi": {
        "name": "Comexi Group",
        "uri": "https://www.comexi.com"
    },
    "starlinger": {
        "name": "Starlinger & Co GmbH",
        "uri": "https://www.starlinger.com"
    },
    "grundfos": {
        "name": "Grundfos Holding A/S",
        "uri": "https://www.grundfos.com"
    },
    "ksb": {
        "name": "KSB SE & Co. KGaA",
        "uri": "https://www.ksb.com"
    },
    "pentair": {
        "name": "Pentair plc",
        "uri": "https://www.pentair.com"
    },
    "caldwell": {
        "name": "Caldwell Tanks Inc.",
        "uri": "https://www.caldwelltanks.com"
    },
    "cb_i": {
        "name": "CB&I Storage Solutions",
        "uri": "https://www.cbi.com"
    }
}

# Machine models by type
machine_models = {
    "Press": {
        "heidelberg": ["Speedmaster XL 106", "Printmaster QM 46", "Versafire EP"],
        "komori": ["Lithrone GX40", "Enthrone 29", "Impremia NS40"]
    },
    "Lam": {
        "bobst": ["NOVACUT 106 E", "MASTERCUT 106 PER", "VISIONFOLD 110 A"],
        "atlas": ["Titan SR3", "Titan SR5", "Convert-O-Matic"]
    },
    "Slit": {
        "atlas": ["Titan SR8", "Phoenix SR2", "Maximus SR6"],
        "comexi": ["S1 DT", "S1 Offset", "S1 Smart"]
    },
    "Bag": {
        "starlinger": ["type recoSTAR PET 330 HC iV+", "type recycling line PET", "type recoSTAR universal 165 iV+"],
        "comexi": ["CT flexo CI8", "ML combi", "F2 MB flexo"]
    },
    "Pump": {
        "grundfos": ["CR 32-4-2", "TPE 32-120/4", "NK 65-125/124"],
        "ksb": ["Omega 65-125", "Etanorm 65-125", "Multitec 40/4"]
    },
    "Pumping_Station": {
        "grundfos": ["Hydro MPC-S 3 CR32", "Hydro Multi-E 3 CR64", "Hydro Multi-S P 3CR32"],
        "pentair": ["Aurora 408GT", "Pentair Myers 3085", "Berkeley B4FRBM"]
    },
    "Tank": {
        "caldwell": ["Pedesphere 100000", "Freedom 75000", "Aquastore 50000"],
        "cb_i": ["Fixed Roof 200000", "Floating Roof 500000", "Pressure Vessel 25000"]
    }
}


def generate_machine_payload(machine_type, mqtt_topic):
    """Generate a complete machine identification payload."""
    # Select random manufacturer and model
    available_manufacturers = list(machine_models[machine_type].keys())
    manufacturer_key = random.choice(available_manufacturers)
    manufacturer_data = manufacturers[manufacturer_key]
    model = random.choice(machine_models[machine_type][manufacturer_key])
    
    # Generate dates
    construction_date = generate_construction_date()
    operation_date = generate_operation_date(construction_date)
    software_date = generate_operation_date(construction_date)
    
    # Generate unique identifiers
    asset_id = f"{mqtt_topic.upper()}-{random.randint(1000, 9999)}"
    serial_number = f"{manufacturer_key.upper()[:3]}{random.randint(100000, 999999)}"
    product_code = f"PC-{model.replace(' ', '-').upper()}-{random.randint(100, 999)}"
    
    # Machine type display names
    machine_display_names = {
        "Press": "Printing Press",
        "Lam": "Laminator", 
        "Slit": "Slitter",
        "Bag": "Bag Machine",
        "Pump": "Pump",
        "Pumping_Station": "Pumping Station",
        "Tank": "Tank"
    }
    display_name = machine_display_names[machine_type]
    
    payload = {
        "MachineIdentificationType": {
            "AssetId": asset_id,
            "ComponentName": f"{display_name} {asset_id}",
            "DefaultInstanceBrowseName": f"/{mqtt_topic}/{asset_id}",
            "DeviceClass": f"Industrial {display_name}",
            "DeviceManual": f"{manufacturer_data['uri']}/manuals/{model.replace(' ', '-').lower()}",
            "DeviceRevision": f"Rev-{random.randint(1, 5)}.{random.randint(0, 9)}",
            "HardwareRevision": f"HW-{random.randint(1, 3)}.{random.randint(0, 9)}",
            "InitialOperationDate": operation_date.isoformat() + "Z",
            "Location": random.choice(["Production Floor A", "Manufacturing Line 1", "Assembly Bay 3", "Processing Unit 2"]),
            "Manufacturer": manufacturer_data["name"],
            "ManufacturerUri": manufacturer_data["uri"],
            "ProductInstanceUri": f"{manufacturer_data['uri']}/products/{model.replace(' ', '-').lower()}",
            "Model": model,
            "MonthOfConstruction": construction_date.month,
            "YearOfConstruction": construction_date.year,
            "PatchIdentifiers": [f"PATCH-{random.randint(100, 999)}" for _ in range(random.randint(0, 3))],
            "RevisionCounter": random.randint(0, 5),
            "ProductCode": product_code,
            "SerialNumber": serial_number,
            "SoftwareReleaseDate": software_date.isoformat() + "Z",
            "SoftwareRevision": f"SW-{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "UI Element": f"{machine_type.lower()}_control_panel_{asset_id.lower()}"
        }
    }
    
    return payload


def main():
    """Generate sample payloads for all machine types or a specific type."""
    parser = argparse.ArgumentParser(
        description='Generate sample machine identification payloads',
        epilog='Examples:\n'
               '  python3 generate_sample_payloads.py           # Generate all machine types\n'
               '  python3 generate_sample_payloads.py press     # Generate 1 Printing Press\n'
               '  python3 generate_sample_payloads.py press 3   # Generate 3 Printing Press payloads\n'
               '  python3 generate_sample_payloads.py LAM 5     # Generate 5 Laminator payloads\n'
               '  python3 generate_sample_payloads.py Slit      # Generate 1 Slitter payload\n'
               '  python3 generate_sample_payloads.py bag 2     # Generate 2 Bag Machine payloads\n'
               '  python3 generate_sample_payloads.py pump      # Generate 1 Pump payload\n'
               '  python3 generate_sample_payloads.py pumping_station 3  # Generate 3 Pumping Station payloads\n'
               '  python3 generate_sample_payloads.py tank 2    # Generate 2 Tank payloads',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('machine_type', nargs='?', 
                       help='Specific machine type to generate (press, lam, slit, bag, pump, pumping_station, tank - case insensitive)')
    parser.add_argument('count', nargs='?', type=int, default=1,
                       help='Number of payloads to generate (default: 1)')
    
    args = parser.parse_args()
    
    machine_types = [
        ("Press", "Press"),
        ("Lam", "Lam"),
        ("Slit", "Slit"),
        ("Bag", "Bag"),
        ("Pump", "Pump"),
        ("Pumping_Station", "Pumping_Station"),
        ("Tank", "Tank")
    ]
    
    machine_display_names = {
        "Press": "Printing Press",
        "Lam": "Laminator", 
        "Slit": "Slitter",
        "Bag": "Bag Machine",
        "Pump": "Pump",
        "Pumping_Station": "Pumping Station",
        "Tank": "Tank"
    }
    
    # Valid machine type mapping (case-insensitive)
    valid_machine_types = {
        "press": "Press",
        "lam": "Lam", 
        "slit": "Slit",
        "bag": "Bag",
        "pump": "Pump",
        "pumping_station": "Pumping_Station",
        "tank": "Tank"
    }
    
    # Validate count parameter
    if args.count is not None and args.count < 1:
        print(f"Error: Count must be a positive integer (got {args.count})", file=sys.stderr)
        sys.exit(1)
    
    # If specific machine type is requested, generate that type and print to console
    if args.machine_type:
        machine_input = args.machine_type.lower()
        if machine_input not in valid_machine_types:
            print(f"Error: Invalid machine type '{args.machine_type}'. Valid options: press, lam, slit, bag, pump, pumping_station, tank (case insensitive)", file=sys.stderr)
            sys.exit(1)
        
        machine_type = valid_machine_types[machine_input]
        mqtt_topic = machine_type
        display_name = machine_display_names[machine_type]
        
        # Generate multiple payloads if count > 1
        for i in range(args.count):
            payload = generate_machine_payload(machine_type, mqtt_topic)
            
            if args.count > 1:
                print(f"=== {display_name} Payload {i + 1} of {args.count} ===")
            
            print(json.dumps(payload, indent=2))
        
        return
    
    # Generate all machine types and save to files
    # Create machines directory if it doesn't exist
    os.makedirs('machines', exist_ok=True)
    
    for machine_type, mqtt_topic in machine_types:
        display_name = machine_display_names[machine_type]
        payload = generate_machine_payload(machine_type, mqtt_topic)
        
        print(f"\n=== {display_name} ({mqtt_topic}) Sample Payload ===")
        print(json.dumps(payload, indent=2))
        print("-" * 60)
        
        # Save individual machine payload to machines folder
        individual_filename = f'machines/{mqtt_topic.lower()}.json'
        with open(individual_filename, 'w') as f:
            json.dump(payload, f, indent=2)
        print(f"Individual payload saved to '{individual_filename}'")
    
    print(f"\nAll individual machine files saved to 'machines/' folder")


if __name__ == "__main__":
    main()