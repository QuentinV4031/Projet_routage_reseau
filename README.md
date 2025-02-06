# Projet_routage_reseau

Ce projet vise à automatiser la génération de configurations Cisco pour un réseau simulé dans GNS3. Le script Python (Script_Q.py) lit un fichier JSON (intent_file.json) contenant la configuration du réseau, génère les configurations pour chaque routeur, et les copie dans les répertoires appropriés pour une utilisation dans GNS3.

## Fonctionnalités
## Ce qui fonctionne :
### Lecture du fichier JSON :

Le script lit correctement le fichier intent_file.json pour extraire les informations sur les routeurs, les AS (Autonomous Systems), les interfaces, les protocoles IGP (RIP, OSPF), et les politiques BGP.

### Génération des configurations Cisco :

Le script génère des configurations Cisco pour chaque routeur en fonction des informations fournies dans le fichier JSON.

#### Les configurations incluent :

Configuration de base (hostname, IPv6, etc.).

Configuration des interfaces (adresses IP, activation IPv6, etc.).

Configuration des protocoles IGP (RIP ou OSPF) sur les interfaces appropriées.

Configuration des sessions BGP (iBGP et eBGP) avec les politiques de routage (peer, client, provider).

### Gestion des politiques BGP :

Le script applique les politiques BGP définies dans le fichier JSON (peer, client, provider) en utilisant des route-map et des prefix-list.

Copie des configurations dans les répertoires :

Le script copie les fichiers de configuration générés dans les répertoires spécifiés pour chaque routeur, ce qui permet une intégration facile avec GNS3.

### Gestion des erreurs :

Le script vérifie si un répertoire est configuré pour chaque routeur. Si aucun répertoire n'est trouvé, un message d'avertissement est affiché.

Ce qui ne fonctionne pas ou nécessite des améliorations :
Gestion des erreurs dans le fichier JSON :

Le script ne vérifie pas si le fichier JSON est bien formé ou s'il contient des erreurs. Si le fichier JSON est mal formaté, le script peut planter.

### Gestion des erreurs de connexion BGP :

Le script ne vérifie pas si les adresses IP des voisins BGP sont valides ou accessibles. Cela pourrait entraîner des erreurs lors de la configuration des routeurs.

### Gestion des zones OSPF :

Le script configure OSPF avec une zone fixe (area 0). Il serait préférable de permettre la configuration de différentes zones OSPF en fonction des besoins du réseau.

### Gestion des routeurs supplémentaires :

Le script ne génère pas de configurations pour les routeurs R13 et R14 (s'ils existent), car ils ne sont pas définis dans le fichier JSON. Il serait utile d'ajouter une gestion dynamique des routeurs supplémentaires.

### Gestion des adresses IPv4 :

Le script est entièrement axé sur IPv6. Si des configurations IPv4 sont nécessaires, elles ne sont pas prises en charge actuellement.

### Gestion des erreurs de copie :

Le script ne vérifie pas si les répertoires de destination existent avant de copier les fichiers. Si un répertoire n'existe pas, une erreur pourrait survenir.

### Gestion des relations BGP complexes :

Le script ne gère pas les relations BGP complexes telles que les route-reflectors ou les confédérations BGP.

## Utilisation
### Prérequis :

Python 3.x installé.

Un fichier JSON (intent_file.json) contenant la configuration du réseau.

Des répertoires configurés pour chaque routeur dans router_directories.

### Exécution du script :

Placez le fichier intent_file.json dans le même répertoire que le script Script_Q.py ou modifiez le chemin d'accès dans le script.

### Exécutez le script avec la commande suivante :
  python Script_Q.py
Les configurations générées seront copiées dans les répertoires spécifiés.

### Intégration avec GNS3 :

Importez les configurations générées dans GNS3 pour chaque routeur.

Démarrez les routeurs et vérifiez la connectivité et les politiques de routage.


## Améliorations possibles
Ajouter la gestion des erreurs pour le fichier JSON.

Permettre la configuration des zones OSPF dynamiques.

Ajouter la prise en charge d'IPv4.

Gérer les relations BGP complexes (route-reflectors, confédérations).

Ajouter des tests unitaires pour vérifier la validité des configurations générées.

## Conclusion
Ce script est un bon point de départ pour automatiser la génération de configurations Cisco pour un réseau simulé dans GNS3. Cependant, il nécessite des améliorations pour gérer des scénarios plus complexes et pour être plus robuste en termes de gestion des erreurs.
