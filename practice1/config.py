from netmiko import ConnectHandler 
# Router connection details 
router = { 
"device_type": "cisco_ios", 
"host": "192.168.177.131", # replace with your router's IP 
"username": "ramesh", 
"password": "cisco123", 
"secret": "cisco123",
# enable password (same as user for now) 
} 
# Connect to router 
connect = ConnectHandler(**router) 
connect.enable() 
config_comm = [
    "interface loopback 10",
    "ip address 10.10.10.10 255.255.255.255"
    
]
# Run command 
output = connect.send_config_set(config_comm) 
output = connect.send_command("show ip int brief")
print(output) 
# Disconnect 
connect.disconnect() 