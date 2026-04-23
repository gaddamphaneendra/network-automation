import yaml
import logging
from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException

# Configure logging
logging.basicConfig(
    filename="health_check.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load devices from YAML inventory
with open("inventory.yml") as file:
    devices = yaml.safe_load(file)["devices"]

# Iterate through each device
for device in devices:
    host = device["host"]
    print(f"\n🔗 Connecting to {host}...")

    try:
        connection = ConnectHandler(**device)
        connection.enable()

        # OSPF check
        ospf_output = connection.send_command("show ip ospf neighbor")
        if "FULL" in ospf_output:
            print("✅ OSPF OK")
            logging.info(f"{host} - OSPF OK")
        else:
            print("⚠️ OSPF ISSUE")
            logging.warning(f"{host} - OSPF ISSUE")

        # BGP check
        bgp_output = connection.send_command("show ip bgp summary")
        if "Establ" in bgp_output or "Established" in bgp_output:
            print("✅ BGP OK")
            logging.info(f"{host} - BGP OK")
        else:
            print("❌ BGP DOWN")
            logging.warning(f"{host} - BGP DOWN")

        connection.disconnect()

    except NetmikoTimeoutException:
        print("❌ Device not reachable")
        logging.error(f"{host} - Timeout")

    except NetmikoAuthenticationException:
        print("❌ Authentication failed")
        logging.error(f"{host} - Authentication failed")
