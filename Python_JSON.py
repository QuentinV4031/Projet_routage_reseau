import json
import networkx as nx

# Charger le fichier JSON contenant la configuration du réseau
with open('c:/Users/K3605/Desktop/TC/GNS/Projet_routage_reseau/JSON_GNS.json', 'r') as file:
    network_config = json.load(file)


# Créer une représentation graphique du réseau avec NetworkX
G = nx.Graph()

# Fonction pour générer la configuration Cisco d'un routeur
def generate_cisco_config(router):
    config = []
    config.append(f"hostname {router['router']}")
    config.append("!")
    config.append("interface Loopback0")
    config.append(f" ip address {router['loopback']}" if ':' not in router['loopback'] else f" ipv6 address {router['loopback']}")
    config.append("!")

    # Configurer les interfaces
    for connection in router['connections']:
        config.append(f"interface {connection['interface']}")
        if ':' in connection['ip']:
            config.append(f" ipv6 address {connection['ip']}")
        else:
            config.append(f" ip address {connection['ip']}")
        config.append(" no shutdown")
        config.append("!")

    # Configurer les protocoles IGP
    as_number = network_config['as_numbers'][router['as']]
    igp_protocol = network_config['protocols']['igp'][router['as']]
    if igp_protocol == "RIP":
        config.append("router rip")
        config.append(" version 2")
        config.append(f" network {'.'.join(router['loopback'].split('.')[:3])}.0")
    elif igp_protocol == "OSPF":
        config.append("router ospf 1")
        config.append(f" router-id {router['loopback'].split('/')[0]}")
        for connection in router['connections']:
            if ':' not in connection['ip']:
                config.append(f" network {'.'.join(connection['ip'].split('.')[:3])}.0 0.0.0.255 area 0")
    config.append("!")

    # Configurer les sessions BGP
    for bgp in network_config['protocols']['bgp']:
        if bgp['router'] == router['router']:
            config.append(f"router bgp {bgp['as_number']}")
            for neighbor in bgp['neighbors']:
                config.append(f" neighbor {neighbor['neighbor']} remote-as {neighbor['remote_as']}")
            config.append("!")

    return '\n'.join(config)

# Ajouter les routeurs et générer leurs configurations
for router in network_config['architecture']:
    router_name = router['router']
    G.add_node(router_name, asn=network_config['as_numbers'][router['as']], loopback=router['loopback'])

    # Ajouter les connexions entre les routeurs
    for connection in router['connections']:
        G.add_edge(router_name, connection['to'], interface=connection['interface'], peer_interface=connection['peer_interface'], ip=connection['ip'], peer_ip=connection['peer_ip'])

    # Générer la configuration Cisco pour chaque routeur
    config = generate_cisco_config(router)
    config_filename = f"{router_name}_config.txt"
    with open(config_filename, 'w') as config_file:
        config_file.write(config)
    print(f"Configuration générée pour {router_name} dans {config_filename}")

# Visualisation du graphe pour validation
import matplotlib.pyplot as plt
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10)
plt.show()
