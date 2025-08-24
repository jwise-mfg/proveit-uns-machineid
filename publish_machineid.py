#!/usr/bin/env python3
"""
Generate machine identification payloads based on a configuration file and publish to MQTT broker.
Uses the existing generate_sample_payloads.py script to create payloads and publishes to specified topics.
"""

import argparse
import json
import sys
import subprocess
import time
try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Error: paho-mqtt library is required. Install with: pip install paho-mqtt", file=sys.stderr)
    sys.exit(1)


def load_config(config_path):
    """Load and validate the configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required structure
        if 'mqtt_broker' not in config:
            raise ValueError("Config file must contain 'mqtt_broker' section")
        
        if 'machines' not in config:
            raise ValueError("Config file must contain a 'machines' array")
        
        if not isinstance(config['machines'], list):
            raise ValueError("'machines' must be an array")
        
        # Validate MQTT broker config
        broker_config = config['mqtt_broker']
        required_broker_fields = ['host', 'port']
        for field in required_broker_fields:
            if field not in broker_config:
                raise ValueError(f"MQTT broker config missing required field: {field}")
        
        # Validate each machine entry
        for i, machine in enumerate(config['machines']):
            if not isinstance(machine, dict):
                raise ValueError(f"Machine entry {i} must be an object")
            
            if 'type' not in machine:
                raise ValueError(f"Machine entry {i} missing required 'type' field")
            
            if 'topic' not in machine:
                raise ValueError(f"Machine entry {i} missing required 'topic' field")
        
        return config
    
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid config file structure: {e}", file=sys.stderr)
        sys.exit(1)


def generate_machine_payload(machine_type):
    """Call the existing generate_sample_payloads.py script to generate a payload."""
    try:
        result = subprocess.run(
            ['python3', 'generate_sample_payloads.py', machine_type],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error generating payload for {machine_type}: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output for {machine_type}: {e}", file=sys.stderr)
        return None


class MQTTPublisher:
    """MQTT client wrapper for publishing machine payloads."""
    
    def __init__(self, broker_config, verbose=False):
        self.broker_config = broker_config
        self.verbose = verbose
        self.client = None
        self.connected = False
        self.publish_results = {}
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self.connected = True
            if self.verbose:
                print(f"Connected to MQTT broker {self.broker_config['host']}:{self.broker_config['port']}")
        else:
            print(f"Failed to connect to MQTT broker. Return code: {rc}", file=sys.stderr)
    
    def on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        self.publish_results[mid] = True
        if self.verbose:
            print(f"  Message published successfully (mid: {mid})")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self.connected = False
        if self.verbose:
            print("Disconnected from MQTT broker")
    
    def connect(self):
        """Connect to the MQTT broker."""
        try:
            self.client = mqtt.Client(
                client_id=self.broker_config.get('client_id', 'machine_payload_publisher'),
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1
            )
            self.client.on_connect = self.on_connect
            self.client.on_publish = self.on_publish
            self.client.on_disconnect = self.on_disconnect
            
            # Set username/password if provided
            if self.broker_config.get('username') and self.broker_config.get('password'):
                self.client.username_pw_set(self.broker_config['username'], self.broker_config['password'])
            
            # Connect to broker
            self.client.connect(
                self.broker_config['host'], 
                self.broker_config['port'], 
                self.broker_config.get('keepalive', 60)
            )
            
            # Start the client loop
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            if not self.connected:
                raise Exception("Connection timeout")
                
            return True
            
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}", file=sys.stderr)
            return False
    
    def publish(self, topic, payload, timeout=30):
        """Publish a payload to the specified topic."""
        if not self.connected:
            print("Not connected to MQTT broker", file=sys.stderr)
            return False
        
        try:
            # Convert payload to JSON string
            payload_json = json.dumps(payload)
            
            # Publish message
            result = self.client.publish(
                topic, 
                payload_json,
                qos=self.broker_config.get('qos', 0),
                retain=self.broker_config.get('retain', False)
            )
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Failed to publish to topic {topic}. Return code: {result.rc}", file=sys.stderr)
                return False
            
            # Wait for publish confirmation
            mid = result.mid
            self.publish_results[mid] = False
            
            wait_time = 0
            while not self.publish_results[mid] and wait_time < timeout:
                time.sleep(0.1)
                wait_time += 0.1
            
            if self.publish_results[mid]:
                return True
            else:
                print(f"Publish timeout for topic {topic}", file=sys.stderr)
                return False
                
        except Exception as e:
            print(f"Error publishing to topic {topic}: {e}", file=sys.stderr)
            return False
    
    def disconnect(self):
        """Disconnect from the MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()


def main():
    """Generate machine payloads and publish to MQTT broker based on configuration file."""
    parser = argparse.ArgumentParser(
        description='Generate machine identification payloads and publish to MQTT broker',
        epilog='Examples:\n'
               '  python3 publish_machineid.py                       # Use default publish_config.json\n'
               '  python3 publish_machineid.py my_config.json        # Use custom config file\n'
               '  python3 publish_machineid.py -v config.json        # Verbose output\n'
               '  python3 publish_machineid.py --dry-run             # Test without publishing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('config_file', nargs='?', default='publish_config.json',
                       help='Configuration file path (default: publish_config.json)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate payloads but do not publish to MQTT')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.verbose:
        print(f"Loading configuration from: {args.config_file}")
    
    config = load_config(args.config_file)
    global_settings = config.get('global_settings', {})
    
    # Initialize MQTT publisher if not dry run
    publisher = None
    if not args.dry_run:
        if args.verbose:
            print("Connecting to MQTT broker...")
        
        publisher = MQTTPublisher(config['mqtt_broker'], args.verbose)
        if not publisher.connect():
            print("Failed to connect to MQTT broker", file=sys.stderr)
            sys.exit(1)
    
    try:
        # Process each machine in the config
        total_machines = len(config['machines'])
        successful_publications = 0
        
        for i, machine_config in enumerate(config['machines'], 1):
            machine_type = machine_config['type']
            topic = machine_config['topic']
            
            if args.verbose:
                print(f"\n[{i}/{total_machines}] Processing {machine_type}...")
            
            # Generate the machine payload
            payload = generate_machine_payload(machine_type)
            if payload is None:
                print(f"Failed to generate payload for {machine_type}", file=sys.stderr)
                continue
            
            # Check if topic ends with MachineIdentificationType and adjust payload accordingly
            publish_payload = payload
            if topic.endswith('MachineIdentificationType'):
                # Remove the outer wrapper and publish just the inner content
                publish_payload = payload['MachineIdentificationType']
            
            if args.dry_run:
                # Just show what would be published
                asset_id = payload['MachineIdentificationType']['AssetId']
                wrapper_note = " (outer wrapper removed)" if topic.endswith('MachineIdentificationType') else ""
                print(f"Would publish {machine_type} payload (Asset ID: {asset_id}) to topic: {topic}{wrapper_note}")
                successful_publications += 1
            else:
                # Publish to MQTT broker with retry logic
                publish_timeout = global_settings.get('publish_timeout', 30)
                retry_attempts = global_settings.get('retry_attempts', 3)
                retry_delay = global_settings.get('retry_delay', 1)
                
                published = False
                for attempt in range(retry_attempts):
                    if args.verbose and attempt > 0:
                        print(f"  Retry attempt {attempt + 1}/{retry_attempts}")
                    
                    if publisher.publish(topic, publish_payload, publish_timeout):
                        asset_id = payload['MachineIdentificationType']['AssetId']
                        wrapper_note = " (outer wrapper removed)" if topic.endswith('MachineIdentificationType') else ""
                        if args.verbose:
                            print(f"  Published {machine_type} payload (Asset ID: {asset_id}) to topic: {topic}{wrapper_note}")
                        else:
                            print(f"Published {machine_type} to {topic}")
                        successful_publications += 1
                        published = True
                        break
                    
                    if attempt < retry_attempts - 1:
                        time.sleep(retry_delay)
                
                if not published:
                    print(f"Failed to publish {machine_type} after {retry_attempts} attempts", file=sys.stderr)
        
        # Summary
        if args.verbose:
            print(f"\n=== Summary ===")
            print(f"Total machines processed: {total_machines}")
            print(f"Successful {'publications' if not args.dry_run else 'generations'}: {successful_publications}")
            print(f"Failed {'publications' if not args.dry_run else 'generations'}: {total_machines - successful_publications}")
        
        if successful_publications == 0:
            action = "published" if not args.dry_run else "generated"
            print(f"No machine payloads were {action} successfully", file=sys.stderr)
            sys.exit(1)
        elif successful_publications < total_machines:
            action = "published" if not args.dry_run else "generated" 
            print(f"Warning: Only {successful_publications}/{total_machines} payloads {action} successfully", file=sys.stderr)
            sys.exit(1)
        else:
            if args.verbose:
                action = "published" if not args.dry_run else "generated"
                print(f"All machine payloads {action} successfully!")
    
    finally:
        # Clean up MQTT connection
        if publisher:
            publisher.disconnect()


if __name__ == "__main__":
    main()