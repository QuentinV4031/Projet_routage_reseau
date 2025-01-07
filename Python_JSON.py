import json
import networkx as nx

# Charger le fichier JSON contenant la configuration du réseau
with open('JSON_GNS.json', 'r') as file:
    network_config = json.load(file)

# Créer une représentation graphique du réseau avec NetworkX
G = nx.Graph()

# Ajouter les routeurs
for router in network_config['architecture']:
    router_name = router['router']
    G.add_node(router_name, asn=network_config['as_numbers'][router['as']], loopback=router['loopback'])
    
    # Ajouter les connexions entre les routeurs
    for connection in router['connections']:
        G.add_edge(router_name, connection['to'], interface=connection['interface'],peer_interface=connection['peer_interface'], ip=connection['ip'], peer_ip=connection['peer_ip'])

# Configuration des protocoles IGP
for asn, protocol in network_config['protocols']['igp'].items():
    routers_in_as = [r['router'] for r in network_config['architecture'] if r['as'] == asn]
    print(f"Configurer le protocole IGP {protocol} pour l'AS {asn} avec les routeurs {', '.join(routers_in_as)}")

# Configuration BGP
for bgp in network_config['protocols']['bgp']:
    router = bgp['router']
    as_number = bgp['as_number']
    neighbors = bgp['neighbors']
    print(f"Configurer BGP sur le routeur {router} avec l'AS {as_number}")
    for neighbor in neighbors:
        print(f"  - Voisin {neighbor['neighbor']} avec l'AS {neighbor['remote_as']}")

# Affichage du graphe pour validation
import matplotlib.pyplot as plt
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10)
plt.show()
