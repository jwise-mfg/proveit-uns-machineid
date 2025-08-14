# Standardizing Machine Identification

This project reflects the VDMA standard Machine Building Block for Machine Identification as JSON. 
The included python scripts generate payloads that can be included in a MQTT broker. 

- To learn more about the VDMA Machine Building block standards, please visit [umati.org](https://umati.org/industries_machinery/)
- To join the community advocating for, and helping to improve, open industrial information standards, please visit [cesmii.org](https://www.cesmii.org)
- To attend the next ProveIt event, check out [proveitconference.com](https://www.proveitconference.com/)
- Vibe coded by Jonathan Wise and Claude -- you can see the prompts I used to build this project in [prompts.txt](prompts.txt)
- Need help standardizing your UNS or other information models? Visit [theoremsystems.com](https://www.theoremsystems) or look me up on LinkedIn!

## Usage

Run the Python script to generate new sample payloads:

```bash
# Generate all machine types and save to files in the "machines" folder
python3 generate_sample_payloads.py

# Generate specific machine type (outputs to console)
python3 generate_sample_payloads.py press
python3 generate_sample_payloads.py lam
python3 generate_sample_payloads.py slit  
python3 generate_sample_payloads.py bag

# Generate multiple payloads of the same type (outputs to console)
python3 generate_sample_payloads.py press 3
python3 generate_sample_payloads.py lam 5
```

**Output Options:**
- **No arguments**: Creates individual machine files in `machines/` directory
- **Machine type only**: Prints single payload to console as JSON
- **Machine type + count**: Prints multiple payloads to console with separation headers

**Features:**
- Machine type arguments are case-insensitive (`press`, `PRESS`, `Press` all work)
- Generated payloads include realistic manufacturer data, model names, and date constraints
- Multiple payloads are clearly separated with headers for easy parsing

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

### MQTT Topics

1. Press
2. Lam
3. Slit
4. Bag