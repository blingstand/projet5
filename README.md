#Projet5#

Cette partie est destinée à l'utilisateur.

Le projet 5bis est un projet réalisé dans le cadre de la formation Openclassroom,
parcours développement d'application Python/Django que je réalise.

Dans ce projet il s'agit de créer une application sur console qui va récupérer des
informations d'un utilisateur pour mener à bien une recherche sur un site internet
(Open Food Fact). Pour cela il fait appel à une API, il télécharge 400 produits, soient
20 catégories contenant chacunes 20 produits. L'utilisateur pourra donc utiliser l'application
pour essayer de trouver un substitutt à un produit qu'il aura choisi. Il aura de plus accès
à un système d'identification qui gèrera l'historique des recherches


Il s'agit d'une version prototypique, une interface graphique est à venir ainsi que de
nouvelles fonctionnalité pour améliorer le confort d'utilisation.


**Comment ça marche**

1. ouvrir votre console,
2. aller dans le fichier du projet 5bis,
3. créer un environnement virtuel, "virtualenv/env" par exemple
4. dans le terminal écrire : "pip install git+https://github.com/openfoodfacts/openfoodfacts-python"
5. puis encore : pip install -r lib.txt (intalle les librairies restantes)
6. créer la base de donnée mysql qui se trouve dans le dossier db/,
5. lancer main.py,
6. suivre les indications.

*Note :*
    * Chaque utilisateur doit disposer d'un pseudo et d'un mot de passe. Pour chaque action,
    le programme vérifiera vos identifiants, à l'exception de la recherche de substitut.
    En effet celle-ci ne vous demandera de vous identifier que si vous souhaitez enregistrer
    le résultat de la recherche.
    * Le projet ne propose pas actuellement de procédé de récupération d'identifiants. Pensez donc
    à bien noter vos identifiants. Ces améliorations seront présentes dans la version 1.2 à venir.


**Informations techniques**

version de Python utilisée : 3.7.1rc1

contenu de mon environnement virtuel :
* certifi==2019.3.9
* chardet==3.0.4
* idna==2.8
* mysql-connector==2.2.9
* mysql-connector-python==8.0.16
* openfoodfacts==0.1.0
* protobuf==3.8.0
* requests==2.22.0
* six==1.12.0
* urllib3==1.25.3


- - - - - - -
Cette partie est destinée aux développeurs, en plus des nombreux doctypes et commentaires. Il leur permet
de se familiariser avec l'app avant de se plonger dans le code.

**main.py**
Lance toutes les actions à partir du choix pris par l'utilisateur.
Propose 4 choix :
1. Me connecter/déconnecter
2. Trouver un substitut,
3. Consulter l'historique de recherche,
4. Quitter.
Affiche à tout moment l'état de connexion de l'utilisateur et son pseudo.

**find_sub.py**
Permet de lancer une recherche avec l'API de OFF.
Crée une instance de la classe search, qui crée elle-même une instance de la classe Substitute.
Affiche une présentation du substitut ainsi que sa description.
Propose d'enregistrer les résultats

**db_user.py**
Permet de lancer plusieurs fonction en rapport avec l'utilisateur:
1. inscription,
2. connection,
3. authentication, propose à l'utilisateur de s'inscrire ou de se connecter
4. history,

**user.py**
Permet la création de l'utilisateur.

**database.py**
Permet de gérer les fonction de recherche, insertion et modification.

**fill_db.py**
Permet d'importer les données de la base OpenFoodFact.

**interactions.py**
Permet de gérer les fonctions qui récupère les infos de l'utilisateur ainsi que vérifier que les saisies correspondent aux attentes.
Toutes ces fonctions reposent sur le principe d'obtention de commandes via des inputs, d'action dans la base via des requêtes sql et d'affichage de réponse via des inputs pour laisser le temps à l'utilisateur de lire le message et d'appuyer sur 'entrer' quand il/elle le juge nécessaire.

** Arborescence **

* main.py
* db/ #contient mon créateur de database ainsi que le script pour importer
    * db_creator.sql
    * fill_db.py
* modules/
    * __init__.py
    * database.py
    * db_user.py
    * user.py
* README.md < vous êtes ici =)
* lib.txt

