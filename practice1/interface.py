from netmiko import ConnectHandler 
# Router connection details 
router = { 
"device_type": "cisco_ios", 
"host": "192.168.177.133", # replace with your router's IP 
"username": "phani", 
"password": "cisco123", 
"secret": "cisco123", 
# enable password (same as user for now) 
} 
# Connect to router 
net_connect = ConnectHandler(**router) 
net_connect.enable() 
# Run command 
output = net_connect.send_command("show ip int brief") 
print(output) 
# Disconnect 
net_connect.disconnect() 