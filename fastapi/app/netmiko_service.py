from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException
from app.logger import logger
import os
from datetime import datetime


def connect_to_device(device):
    conn = ConnectHandler(**device)

    if device.get("secret"):
        conn.enable()

    return conn


def health_check(device):
    try:
        conn = connect_to_device(device)

        ospf_output = conn.send_command(
            "show ip ospf neighbor",
            use_textfsm=True
        )

        bgp_output = conn.send_command(
            "show ip bgp summary",
            use_textfsm=True
        )

        conn.disconnect()

        ospf_status = "PASS"
        bgp_status = "PASS"

        for neighbor in ospf_output:
            neigh_id = neighbor.get("neighbor_id") or neighbor.get("router_id")
            state = neighbor.get("state")

            # Example: FULL/DR -> FULL
            state = state.split("/")[0] if state else "UNKNOWN"

            if state == "FULL":
                print(f"✅ {neigh_id} OSPF FULL")
                logger.info(f"{device['ip']} - {neigh_id} OSPF FULL")
            else:
                print(f"❌ {neigh_id} OSPF NOT FULL ({state})")
                logger.warning(f"{device['ip']} - {neigh_id} OSPF ISSUE ({state})")
                ospf_status = "FAIL"

        for peer in bgp_output:
            neighbor = peer.get("bgp_neighbor")
            state = str(
                peer.get("state_or_prefixes_received")
                or peer.get("state_pfxrcd")
                or "UNKNOWN"
            )


            if state.isdigit():
                print(f"✅ {neighbor} BGP UP ({state} prefixes)")
                logger.info(f"{device['ip']} - {neighbor} BGP OK")
            else:
                print(f"❌ {neighbor} BGP DOWN ({state})")
                logger.warning(f"{device['ip']} - {neighbor} BGP DOWN ({state})")
                bgp_status = "FAIL"

        overall_status = (
            "PASS"
            if ospf_status == "PASS" and bgp_status == "PASS"
            else "FAIL"
        )

        logger.info(
            f"[HEALTH_CHECK] Device {device['ip']} - "
            f"OSPF: {ospf_status}, BGP: {bgp_status}"
        )

        return {
            "ip": device["ip"],
            "status": overall_status,
            "ospf_status": ospf_status,
            "bgp_status": bgp_status,
            "ospf_neighbors": ospf_output,
            "bgp_neighbors": bgp_output
        }

    except NetmikoTimeoutException:
        logger.error(f"[HEALTH_CHECK_TIMEOUT] Device {device['ip']}")

        return {
            "ip": device["ip"],
            "status": "FAIL",
            "error": "Timeout while connecting to device"
        }

    except NetmikoAuthenticationException:
        logger.error(f"[HEALTH_CHECK_AUTH_FAILED] Device {device['ip']}")

        return {
            "ip": device["ip"],
            "status": "FAIL",
            "error": "Authentication failed"
        }

    except Exception as e:
        logger.error(f"[HEALTH_CHECK_FAILED] Device {device['ip']} - {str(e)}")

        return {
            "ip": device["ip"],
            "status": "FAIL",
            "error": str(e)
        }


def backup_config(device):
    try:
        conn = connect_to_device(device)

        running = conn.send_command("show running-config")
        startup = conn.send_command("show startup-config")

        conn.disconnect()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output = f"""
===== BACKUP TIME: {timestamp} =====

===== RUNNING CONFIG =====

{running}


===== STARTUP CONFIG =====

{startup}
"""

        os.makedirs("backups", exist_ok=True)

        filename = f"backups/{device['ip']}_{timestamp}_backup.txt"

        with open(filename, "w") as file:
            file.write(output)

        logger.info(f"[BACKUP] Device {device['ip']} backup saved to {filename}")

        return {
            "ip": device["ip"],
            "status": "success",
            "backup_file": filename
        }

    except NetmikoTimeoutException:
        logger.error(f"[BACKUP_TIMEOUT] Device {device['ip']}")

        return {
            "ip": device["ip"],
            "status": "failed",
            "error": "Timeout while connecting to device"
        }

    except NetmikoAuthenticationException:
        logger.error(f"[BACKUP_AUTH_FAILED] Device {device['ip']}")

        return {
            "ip": device["ip"],
            "status": "failed",
            "error": "Authentication failed"
        }

    except Exception as e:
        logger.error(f"[BACKUP_FAILED] Device {device['ip']} - {str(e)}")

        return {
            "ip": device["ip"],
            "status": "failed",
            "error": str(e)
        }