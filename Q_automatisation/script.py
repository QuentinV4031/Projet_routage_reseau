import json
import networkx as nx

# Charger le fichier JSON contenant la configuration du réseau
with open('intent_file.json', 'r') as file:
    network_config = json.load(file)

# Créer une représentation graphique du réseau avec NetworkX
G = nx.Graph()

print(network_config['architecture'][0]['loopback'])

# Fonction pour générer la configuration Cisco d'un routeur
def generate_cisco_config(router):
    config = []
    router_number=router['router'][1:]
    config.append(f"hostname {router['router']}")
    config.append("!")
    config.append("interface Loopback0")
    config.append(f" ipv6 address {router['loopback']}")
    config.append("!")

    # Déterminer le protocole IGP du routeur
    as_number = network_config['as_numbers'][router['as']]
    igp_protocol = network_config['protocols']['igp'][router['as']]

    # Configurer les interfaces
    for connection in router['connections']:
        config.append(f"interface {connection['interface']}")
        config.append(" no ip address")
        config.append(f" ipv6 address {connection['ip']}")
        config.append(" ipv6 enable")
        config.append(" no shutdown")
        # Activer le protocole IGP sur les interfaces pour les routeurs dans le même AS
        if as_number==connection['peer_as']:
            if igp_protocol=="RIP":
                config.append("ipv6 rip ripng enable")
            if igp_protocol=="OSPF":
                config.append("ipv6 ospf 100 area 0")       #/!\ Ajouter la possibilité de choisir l'area dans l'intent file
        config.append("!")

    # Configurer les protocoles IGP
    if igp_protocol == "RIP":
        config.append("router rip ripng")
        config.append(" redistribute connected")
    elif igp_protocol == "OSPF":
        config.append("router ospf 100")
        config.append(f" router-id {router_number}.{router_number}.{router_number}.{router_number}")
    config.append("!")

    # Configurer les sessions BGP
    config.append(f"router bgp {as_number}")
    config.append(f" bgp router-id {router_number}.{router_number}.{router_number}.{router_number}")
    config.append(" no bgp default ipv4-unicast")
    for connection in router['connections']:
        neighbor_as=network_config['as_numbers'][connection['peer_as']]
        if neighbor_as==as_number:
            config.append(f" neighbor 2000::{connection['to'][1:]} remote-as {neighbor_as}") #configuration ibgp
            config.append(f" neighbor 2000::{connection['to'][1:]} update-source Loopback0")
        else:
            config.append(f" neighbor {connection['peer_ip']} remote-as {neighbor_as}")  #configuration ebgp
    config.append(" !")
    config.append(" address-family ipv6")
    config.append("  redistribute connected") #A remplacer au moment où on fera les bgp policies
    for connection in router['connections']:    #activation des voisins
        neighbor_as=network_config['as_numbers'][connection['peer_as']]
        if neighbor_as==as_number:
            config.append(f"  neighbor 2000::{connection['to'][1:]} activate")
        else:
            config.append(f"  neighbor {connection['peer_ip']} activate")
    config.append(" exit-address-family")
    config.append("!")

    return '\n'.join(config)

# Ajouter les routeurs et générer leurs configurations
for router in network_config['architecture']:
    router_name = router['router']
    G.add_node(router_name, asn=network_config['as_numbers'][router['as']], loopback=router['loopback'])

    # Ajouter les connexions entre les routeurs
    for connection in router['connections']:
        G.add_edge(router_name, connection['to'], interface=connection['interface'], ip=connection['ip'], peer_ip=connection['peer_ip'])

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