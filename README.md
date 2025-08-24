# Standardizing Machine Identification

This project reflects the VDMA standard Machine Building Block for Machine Identification as JSON. 
The included python scripts generate payloads that can be included in a MQTT broker. 

- To join the community advocating for, and helping to improve, open industrial information standards, please visit [cesmii.org](https://www.cesmii.org)
- To learn more about the VDMA Machine Building Block standards, please visit [umati.org](https://umati.org/industries_machinery/)
- To attend the next ProveIt event, check out [proveitconference.com](https://www.proveitconference.com/)
- Vibe coded by Jonathan Wise and Claude -- you can see the prompts I used to build this project in [prompts.txt](prompts.txt)
- Need help standardizing your UNS or other information models? Visit [theoremsystems.com](https://www.theoremsystems) or look me up on [LinkedIn](https://www.linkedin.com/in/jonathanmwise/)!

## Usage

This project requires a recent version of Python3. For MQTT publishing functionality, install the `paho-mqtt` library:

```bash
pip3 install paho-mqtt
```

### Sample Payload Generation

Run the Python script to generate new sample payloads:

```bash
# Generate all machine types and save to files in the "machines" folder
python3 generate_sample_payloads.py

# Generate specific machine type (outputs to console)
python3 generate_sample_payloads.py press
python3 generate_sample_payloads.py lam
python3 generate_sample_payloads.py slit  
python3 generate_sample_payloads.py bag
python3 generate_sample_payloads.py pump
python3 generate_sample_payloads.py pumping_station
python3 generate_sample_payloads.py tank

# Generate multiple payloads of the same type (outputs to console)
python3 generate_sample_payloads.py press 3
python3 generate_sample_payloads.py lam 5
python3 generate_sample_payloads.py pump 2
python3 generate_sample_payloads.py tank 4
```

**Output Options:**
- **No arguments**: Creates individual machine files in `machines/` directory
- **Machine type only**: Prints single payload to console as JSON
- **Machine type + count**: Prints multiple payloads to console with separation headers

**Features:**
- Machine type arguments are case-insensitive (`press`, `PRESS`, `Press` all work)
- Generated payloads include realistic manufacturer data, model names, and date constraints
- Multiple payloads are clearly separated with headers for easy parsing

### MQTT Publishing

Publish machine identification payloads to an MQTT broker using configuration files:

```bash
# Publish using default configuration (publish_config.json)
python3 publish_machineid.py

# Use custom configuration file
python3 publish_machineid.py my_config.json

# Test without actually publishing (dry-run mode)
python3 publish_machineid.py --dry-run

# Verbose output for debugging
python3 publish_machineid.py -v

# Combine options
python3 publish_machineid.py --dry-run -v my_config.json
```

**MQTT Features:**
- Configuration-driven broker connection (host, port, credentials, QoS settings)
- Automatic topic wrapper detection and removal
- Retry logic with configurable attempts and delays
- Dry-run mode for testing configurations
- Support for multiple machines in a single configuration
- Verbose logging for troubleshooting

**Topic Wrapper Handling:**
Topics ending with `MachineIdentificationType` automatically have the outer JSON wrapper removed before publishing, ensuring clean payload structure that matches the topic semantics.

## Broker Implementation

The machine identification payload can be included as a child object within an existing payload or as a subtopic.

### Existing Payload

 If included as a child object in an existing payload, the member name must remain `MachineIdentificationType`:

 `/Your/Machine`:
```
{
    "ExistingDataStructure": {
        "YourData": "",
        "MachineIdentificationType": {
            "AssetId": "Example-1234",
            ...
        }
    }
}
```

### New Sub-Topic

If added as a sub-topic, the topic name must be `MachineIdentificationType` -- which does not need to be repeated within the sub-topic's payload:

`/Your/Machine/MachineIdentificationType`:
```
{
    "AssetId": "Example-1234",
    ...
}
```

## ProveIt UNS

The following information was provided by Walker Reynolds describing the existing machines already on the ProveIt UNS

### Machine Types

1. Printing Press
2. Laminator
3. Slitter
4. Bag Machine
5. Pump
6. Pumping Station
7. Tank

### MQTT Topics

The following machine types map to these MQTT topic identifiers:

1. Press (Printing Press)
2. Lam (Laminator)
3. Slit (Slitter)
4. Bag (Bag Machine)
5. Pump (Simple Pump)
6. Pumping_Station (Complex Pump/Pumping Station)
7. Tank (Liquid Storage Tank)

**Example Configuration:**
```json
{
  "mqtt_broker": {
    "host": "your-broker.com",
    "port": 1883,
    "username": "your-username",
    "password": "your-password"
  },
  "machines": [
    {
      "type": "pump",
      "topic": "factory/utilities/water-system/pump-101/MachineIdentificationType"
    },
    {
      "type": "tank",
      "topic": "factory/storage/tank-201/MachineIdentificationType"
    }
  ]
}
```