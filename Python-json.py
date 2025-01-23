import json
import networkx as nx

# Load the intent file
with open('c:/Users/jerem/Desktop/3TC/GNS/JSON_GNS.json', 'r') as file:
    network_config = json.load(file)

# Create a graph to represent the network
G = nx.Graph()

# Generate Cisco configuration for a router
def generate_cisco_config(router):
    config = [f"hostname {router['router']}", "!"]

    # Configure loopback interface
    loopback_ip = router['loopback']
    config.append("interface Loopback0")
    config.append(f" ip address {loopback_ip}" if ':' not in loopback_ip else f" ipv6 address {loopback_ip}")
    config.append("!")

    # Configure physical interfaces
    for connection in router['connections']:
        interface = connection['interface']
        ip_address = connection['ip']
        config.append(f"interface {interface}")
        config.append(f" ip address {ip_address}" if ':' not in ip_address else f" ipv6 address {ip_address}")
        config.append(" no shutdown")
        config.append("!")

    # Configure IGP (RIP or OSPF)
    igp_protocol = network_config['protocols']['igp'][router['as']]
    if igp_protocol == "RIP":
        config.append("router rip")
        config.append(" version 2")
        config.append(f" network {'.'.join(loopback_ip.split('.')[:3])}.0")
    elif igp_protocol == "OSPF":
        config.append("router ospf 1")
        config.append(f" router-id {loopback_ip.split('/')[0]}")
        for connection in router['connections']:
            if ':' not in connection['ip']:
                network = '.'.join(connection['ip'].split('.')[:3]) + ".0"
                config.append(f" network {network} 0.0.0.255 area 0")
    config.append("!")

    # Configure BGP
    for bgp in network_config['protocols']['bgp']:
        if bgp['router'] == router['router']:
            config.append(f"router bgp {bgp['as_number']}")
            for neighbor in bgp['neighbors']:
                config.append(f" neighbor {neighbor['neighbor']} remote-as {neighbor['remote_as']}")
            config.append("!")

    return '\n'.join(config)

# Connect routers as per the provided scheme
def connect_routers():
    # Get routers in each AS
    as_x_routers = [router for router in network_config['architecture'] if router['as'] == 'AS_X']
    as_y_routers = [router for router in network_config['architecture'] if router['as'] == 'AS_Y']

    # Define specific connections for AS_X based on the diagram
    as_x_links = [
        (0, 1), (0, 2), (1, 2), (1, 5), (2, 6), (6, 4), (5, 3), (6, 3), (5, 4), (5, 6)
    ]
    # Add connections within AS_X
    for link in as_x_links:
        G.add_edge(
            as_x_routers[link[0]]['router'],
            as_x_routers[link[1]]['router'],
            interface=f"Gig0/{link[0]}", 
            peer_interface=f"Gig0/{link[1]}"
        )

    # Define specific connections for AS_Y based on the diagram
    as_y_links = [
        (0, 1), (0, 2), (1, 2), (1, 5), (2, 6), (6, 4), (5, 3), (6, 3), (5, 4), (6, 5)
    ]
    # Add connections within AS_Y
    for link in as_y_links:
        G.add_edge(
            as_y_routers[link[0]]['router'],
            as_y_routers[link[1]]['router'],
            interface=f"Gig0/{link[0]}", 
            peer_interface=f"Gig0/{link[1]}"
        )

    # Establish BGP connections between AS_X and AS_Y
    G.add_edge(as_x_routers[3]['router'], as_y_routers[3]['router'], interface="Gig1/0", peer_interface="Gig1/0")
    G.add_edge(as_x_routers[4]['router'], as_y_routers[4]['router'], interface="Gig1/1", peer_interface="Gig1/1")

# Add routers and generate configurations
for router in network_config['architecture']:
    router_name = router['router']
    G.add_node(router_name, asn=network_config['as_numbers'][router['as']], loopback=router['loopback'])

# Call the function to establish connections as per the topology
connect_routers()

# Generate router configurations
for router in network_config['architecture']:
    config = generate_cisco_config(router)
    config_filename = f"{router['router']}_config.txt"
    with open(config_filename, 'w') as config_file:
        config_file.write(config)
    print(f"Configuration generated for {router['router']} in {config_filename}")

# Visualize the network graph
import matplotlib.pyplot as plt
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10)
plt.show()
