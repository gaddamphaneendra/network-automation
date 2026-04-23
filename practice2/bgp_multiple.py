import yaml
from netmiko import ConnectHandler

# Load YAML inventory
with open("inventory.yml") as file:
    data = yaml.safe_load(file)

routers = data["routers"]

for router, details in routers.items():
    device = {
        "device_type": details["device_type"],
        "ip": details["host"],
        "username": details["username"],
        "password": details["password"]
    }

    print(f"\n Connecting to {router}")

    connection = ConnectHandler(**device)
    config_commands = []

    # Interface configuration
    for interface in details["interfaces"]:
        config_commands.append(f"interface {interface['name']}")
        config_commands.append(f"ip address {interface['ip']} {interface['mask']}")
        config_commands.append("no shutdown")

    # BGP configuration
    config_commands.append(f"router bgp {details['asn']}")
    for neighbor in details["neighbors"]:
        config_commands.append(f"neighbor {neighbor['ip']} remote-as {neighbor['remote_as']}")

    # Push configuration
    output = connection.send_config_set(config_commands)
    print(output)

    # Verify BGP
    print("\n Checking BGP Neighborship...")
    bgp_output = connection.send_command("show ip bgp summary")
    
    print(bgp_output)

    connection.disconnect()

print("\n✅ Automation Completed Successfully")
