import yaml
import logging
from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException

logging.basicConfig(
    filename="health_check.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

with open("inventory.yml") as file:
    devices = yaml.safe_load(file)["devices"]

for device in devices:
    host = device["host"]
    print(f"\n🔗 Connecting to {host}...")

    connection = None

    try:
        connection = ConnectHandler(**device)

        if device.get("secret"):
            connection.enable()

        # OSPF check
        ospf_output = connection.send_command("show ip ospf neighbor",use_textfsm=True)

        for neighbor in ospf_output:
            neigh_id = neighbor.get("neighbor_id") or neighbor.get("router_id")
            state = neighbor.get("state")

             # Some templates give "FULL/DR" → split needed
            state = state.split("/")[0] if state else "UNKNOWN"

            if state =="FULL":
                print(f"✅ {neigh_id} OSPF FULL")
                logging.info(f"{host} - {neigh_id} OSPF FULL")

            else:
                print(f"❌ {neigh_id} OSPF NOT FULL ({state})")
                logging.warning(f"{host} - {neigh_id} OSPF ISSUE ({state})")
                ospf_status = "FAIL"


        # BGP check
        bgp_output = connection.send_command(
            "show ip bgp summary",
            use_textfsm=True
        )

        bgp_status = "PASS"


        for peer in bgp_output:
            neighbor = peer.get("neighbor") 
            state = str(peer.get("state_or_prefixes_received"))

             # ✅ Correct logic
            if state.isdigit():
                print(f"✅ {neighbor} BGP UP ({state} prefixes)")
                logging.info(f"{host} - {neighbor} BGP OK")
                
            else:
                print(f"❌ {neighbor} BGP DOWN ({state})")
                logging.warning(f"{host} - {neighbor} BGP DOWN ({state})")
                bgp_status = "FAIL"

    except NetmikoTimeoutException:
        print("❌ Device not reachable")
        logging.error(f"{host} - Timeout")

    except NetmikoAuthenticationException:
        print("❌ Authentication failed")
        logging.error(f"{host} - Authentication failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"{host} - Error: {e}")

    finally:
        if connection:
            connection.disconnect()