import json
import os
import shutil

# Charger le fichier JSON contenant la configuration du réseau
with open('/home/oggy/GNS_linux/Projet_routage_reseau/intent_file.json', 'r') as file:
    network_config = json.load(file)

# Dictionnaire de correspondance des répertoires pour chaque routeur
router_directories = {
    "R1": "/home/oggy/GNS_linux/Projet_routage_reseau/R1/",
    "R2": "/home/oggy/GNS_linux/Projet_routage_reseau/R2/",
    "R3": "/home/oggy/GNS_linux/Projet_routage_reseau/R3/",
    "R4": "/home/oggy/GNS_linux/Projet_routage_reseau/R4/",
    "R5": "/home/oggy/GNS_linux/Projet_routage_reseau/R5/",
    "R6": "/home/oggy/GNS_linux/Projet_routage_reseau/R6/", #customer
    "R7": "/home/oggy/GNS_linux/Projet_routage_reseau/R7/", #customer
    "R8": "/home/oggy/GNS_linux/Projet_routage_reseau/R8/", 
    "R9": "/home/oggy/GNS_linux/Projet_routage_reseau/R9/",
    "R10": "/home/oggy/GNS_linux/Projet_routage_reseau/R10/",
    "R11": "/home/oggy/GNS_linux/Projet_routage_reseau/R11/",
    "R12": "/home/oggy/GNS_linux/Projet_routage_reseau/R12/", #provider
    "R13": "/home/oggy/GNS_linux/Projet_routage_reseau/R13/", #provider
    # Ajoutez d'autres correspondances si nécessaire
}


# Fonction pour générer la configuration Cisco d'un routeur
def generate_cisco_config(router):
    global network_config

    config = []
    
    router_number=router['router'][1:]
    as_number = network_config['as']['as_numbers'][router['as']]
    igp_protocol = network_config['protocols']['igp'][router['as']]

    config.append("version 15.2")
    config.append("!")
    config.append("no aaa new-model")
    config.append(f"hostname {router['router']}")
    config.append("!")
    config.append("no ip domain lookup")
    config.append("ipv6 unicast-routing")
    config.append("!")
    config.append("ip tcp synwait-time 5")
    config.append("!")
    config.append("interface Loopback0")
    config.append(f" ipv6 address {router['loopback']}/128")
    config.append(" ipv6 enable")
    config.append("!")

    # Configurer les interfaces
    for interface in router['interfaces']:
        config.append(f"interface {interface['interface']}")
        config.append(" no ip address")
        config.append(" negotiation auto")
        config.append(f" ipv6 address {interface['ip']}")
        config.append(" ipv6 enable")
        config.append(" no shutdown")
        # Activer le protocole IGP sur les interfaces pour les routeurs dans le même AS
        if interface['igp']=="True":
            if igp_protocol=="RIP":
                config.append(" ipv6 rip ripng enable")
            if igp_protocol=="OSPF":
                config.append(" ipv6 ospf 100 area 0")       #/!\ Ajouter la possibilité de choisir l'area dans l'intent file
        config.append("!")

    # Configurer les sessions BGP
    config.append(f"router bgp {as_number}")
    config.append(f" bgp router-id {router_number}.{router_number}.{router_number}.{router_number}")
    config.append(" no bgp default ipv4-unicast")
    config.append(" neighbor ibgp peer-group")
    config.append(f" neighbor ibgp remote-as {as_number}")
    config.append(" neighbor ibgp update-source Loopback0")
    config.append(" neighbor ibpg advertisement-interval 1")

    for router_bis in network_config['architecture']:
        if router['as']==router_bis['as'] and router['router']!=router_bis['router']:
            config.append(f" neighbor {router_bis['loopback']} peer-group ibgp") #configuration ibgp
    for neighbor in router['ebgp']:
        neighbor_as_nb=network_config['as']['as_numbers'][neighbor['peer_as']]
        config.append(f" neighbor {neighbor['peer_ip']} remote-as {neighbor_as_nb}")  #configuration ebgp
    config.append(" !")

    config.append(" address-family ipv6")
    config.append("  redistribute connected route-map LOCAL_AS")
    #activation des voisins
    for router_bis in network_config['architecture']:
        if router['as']==router_bis['as'] and router['router']!=router_bis['router']:
            config.append(f"  neighbor {router_bis['loopback']} activate")
    for neighbor in router['ebgp']: 
            config.append(f"  neighbor {neighbor['peer_ip']} activate")
            #bgp policies
            for AS in network_config['protocols']['bgp_policies'][router['as']]:
                if AS['Neighbor']==neighbor['peer_as']:
                    relation = AS['relation']
            if relation=="client":
                config.append(f"  neighbor {neighbor['peer_ip']} route-map ALL out")
            else :
                config.append(f"  neighbor {neighbor['peer_ip']} route-map OUT out")
                
    config.append(" exit-address-family")
    config.append("!")

    # Configurer les protocoles IGP
    if igp_protocol == "RIP":
        config.append("ipv6 router rip ripng")
        config.append(" redistribute connected")
    elif igp_protocol == "OSPF":
        config.append("ipv6 router ospf 100")
        config.append(f" router-id {router_number}0.{router_number}0.{router_number}0.{router_number}0")
        config.append(" redistribute connected")
    config.append("!")

    #configurer les prefix-list
    seq=2
    config.append(f"ipv6 prefix-list LOCAL_AS seq 1 permit {network_config['as']['range'][router['as']]} le 128")
    config.append("!")
    for AS in network_config['protocols']['bgp_policies'][router['as']]:
        if AS['relation']=="peer" or AS['relation']=="provider":
            config.append(f"ipv6 prefix-list PEEROVIDERS_PREFIX seq {seq} permit {network_config['as']['range'][AS['Neighbor']]} le 128")
        if AS['relation']=="client":
            config.append(f"ipv6 prefix-list CLIENTS_PREFIX seq {seq} permit {network_config['as']['range'][AS['Neighbor']]} le 128")
        seq+=1
        config.append("!")

    #configurer les route-map
    config.append("route-map LOCAL_AS permit 4")
    config.append(" match ipv6 address prefix-list LOCAL_PREFIX")
    config.append(" set community 1 additive")
    config.append("!")

    config.append("route-map OUT permit 5")
    config.append(" match ipv6 address prefix-list LOCAL_PREFIX")
    config.append(" set community 2 additive")
    config.append("!")
    config.append("route-map OUT permit 6")
    config.append(" match ipv6 address prefix-list CLIENTS_PREFIX")
    config.append(" set community 2 additive")
    config.append("!")

    config.append("route-map ALL permit 1")
    config.append(" match ipv6 address prefix-list LOCAL_PREFIX")
    config.append(" set community 3 additive")
    config.append("!")
    config.append("route-map ALL permit 2")
    config.append(" match ipv6 address prefix-list CLIENTS_PREFIX")
    config.append(" set community 3 additive")
    config.append("!")
    config.append("route-map ALL permit 3")
    config.append(" match ipv6 address prefix-list PEEROVIDERS_PREFIX")
    config.append(" set community 3 additive")
    config.append("!")
    config.append("end")

    return '\n'.join(config)

# Ajouter les routeurs et générer leurs configurations
for router in network_config['architecture']:
    router_name = router['router']

    # Générer la configuration Cisco pour chaque routeur
    config = generate_cisco_config(router)
    config_filename = f"{router_name}_config.cfg"
    with open(config_filename, 'w') as config_file:
        config_file.write(config)
    print(f"Configuration générée pour {router_name} dans {config_filename}")


   # Copier la configuration dans le répertoire correspondant
    if router_name in router_directories:
        target_directory = router_directories[router_name]
        os.makedirs(target_directory, exist_ok=True)
        shutil.copy(config_filename, target_directory)
        print(f"Configuration copiée dans {target_directory}")
    else:
        print(f"Aucun répertoire configuré pour {router_name}, fichier non copié.")
