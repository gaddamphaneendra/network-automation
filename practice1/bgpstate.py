from netmiko import ConnectHandler 
# Router connection details 
router = { 
"device_type": "cisco_ios", 
"host": "192.168.177.132", # replace with your router's IP 
"username": "phani1", 
"password": "phani123", 
"secret" : "cisco123"
# enable password (same as user for now) 
} 


# BGP states considered "down"
down_states = ["Idle", "Active", "Connect"]

try:
    # Connect to the router
    connection = ConnectHandler(**router)
    connection.enable()

    # Run BGP summary command
    bgp_output = connection.send_command("show ip bgp summary")

    print("\n=== Full BGP Summary Output ===\n")
    print(bgp_output)

    print("\n=== BGP Neighbors which are Down ===\n")

    # Split output into lines
    lines = bgp_output.strip().splitlines()

    # Find header line
    for index, line in enumerate(lines):
        if line.strip().startswith("Neighbor"):
            data_lines = lines[index + 1:]  # Get all data lines after header
            break
    else:
        print("No BGP summary data found.")
        data_lines = []

    # Process neighbor lines
    for line in data_lines:
        if not line.strip():
            continue  # Skip empty lines

        fields = line.split()
        if len(fields) < 9:
            continue  # Not a valid BGP neighbor line

        neighbor_ip = fields[0]
        last_field = fields[-1]
        second_last = fields[-2]

        # Check if neighbor is in a down state
        if last_field in down_states or second_last in down_states:
            print(f"Neighbor {neighbor_ip} is DOWN (State: {last_field})")

    # Close connection
    connection.disconnect()

except Exception as e:
    print(f"Error: {e}")