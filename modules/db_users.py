""" This script contains the database object and all methodes it needs"""

import os
import time
import mysql.connector
from modules.database import Database



def negatif_feed_back(msg):
    """ display a negative feed_back message and let 1sec to read it """
    print("\n", msg, "\n")
    time.sleep(1)

def page(title, supp=None):
    os.system("cls")
    print("\n", "-"*30, " PAGE {} ".format(title), "-"*30, "\n")
    if supp:
        print("- - - - {} - - - -".format(supp))

class DbUser(Database):
    """This class manages the connection to the table user"""

    COLUMNS = 'name, labels, additives, packagings,nutrition_grade, nova_group, traces, '\
    'manufacturing_places_tags, minerals_tags, palm_oil, composition, link, quantity, '\
    'brands, nutriments'


    def _registration(self, user):
        """ checks whether the pseudo is available :
                if yes creates account,
                if not offers 3 possibilities (_connection with these id, start again, exit)  ."""
        if user.pseudo == "":
            user.pseudo = input("\n  Pseudo : ")
            user.password = input("  Mot de passe : ")

        while True:
            # manage the no answer situation
            if user.pseudo == "":
                negatif_feed_back("Fournissez un pseudo !")
                user.pseudo = input("\n  Pseudo : ")
                continue
            if user.password == "":
                negatif_feed_back("Fournissez un mot de passe !")
                user.password = input("  Mot de passe : ")
                continue

            #try is a necessity here to manage the mysql error if the value already exists
            try:
                sql = "INSERT INTO User (pseudo, password) "\
                " VALUES ('{}','{}');".format(user.pseudo, user.password)
                self.my_cursor.execute(sql)
                self.mydb.commit()
                user.connected = True

                #app will need user.id later
                sql = "SELECT id from User WHERE pseudo = '{}'".format(user.pseudo)
                self.my_cursor.execute(sql)
                user_id = self.my_cursor.fetchone()
                user.id = user_id[0]
                return user

            except mysql.connector.errors.IntegrityError:
                # raise e    #for the debug
                print("\nCet identifiant n'est pas disponible :(")

                #Manage the input after no working id, offers 3 possibilities
                while True:
                    answer = input("Peut-être voulez-vous :"\
                        "\n1/ Vous authentifier avec ces identifiants,"\
                        "\n2/ Essayer de nouveau,\n3/ Abandonner.\n ->")

                    if answer == "1":
                        #tries a _connection with these id
                        user = self._connection(user)
                        return user
                    elif answer == "2":
                        #tries again
                        break
                    elif answer == "3":
                        #exits the inscription function
                        user.connected = "Exit"
                        return user
                    negatif_feed_back("Je n'ai pas compris.")
                    continue
            user.pseudo = input("\n  Pseudo : ")
            user.password = input("  Mot de passe : ")

    def _connection(self, user):
        """ checks whether the pseudo is present in the user table.
            if yes creates checks whether the password
                from user table is the same than user.password,
            if not offers 3 possibilities
                (inscription with these id, start again, exit)  ."""
        if user.pseudo == "":
            user.pseudo = input("\n  Pseudo : ")
            user.password = input("  Mot de passe : ")

        loop = True
        while loop:
            sql = "SELECT password FROM user WHERE pseudo = '{}';".format(user.pseudo)
            self.my_cursor.execute(sql)
            resultat = self.my_cursor.fetchone()
            #resultat can be empty or not
            if resultat:
                if resultat[0] == user.password:
                    user.connected = True
                    #app will need user.id later
                    sql = "SELECT id from User WHERE pseudo = '{}';".format(user.pseudo)
                    self.my_cursor.execute(sql)
                    user_id = self.my_cursor.fetchone()
                    user.id = user_id[0]
                    return user
                print("\nMot de passe incorrect ! ")
            else:
                print("\nPseudo inconnu : {} ".format(user.pseudo))

            #if user is not returned start the loop
            while True:
                answer = input("Peut-être voulez-vous :\n1/ Vous inscrire avec ces identifiants,"\
                "\n2/ Essayer de nouveau,\n3/ Abandonner.\n ->")

                if answer == "1":
                    #tries to subscribe with these id
                    user = self._registration(user)
                    return user
                elif answer == "2":
                    #tries again with new id
                    break
                elif answer == "3":
                    #exits the _connection function
                    user.connected = "Exit"
                    return user
                else:
                    negatif_feed_back("Je n'ai pas compris.")
                    continue
            user.pseudo = input("\n  Pseudo : ")
            user.password = input("  Mot de passe : ")

    def authentication(self, user):
        """ connectes a user if user.connected is False

            Therefore it calls inscription() or _connection(),
            depending on the user answer to the input.
            Permits also to get user.id (for the next sql querries will be usefull)
        """

        while not user.connected:
            page("D'AUTHENTIFICATION")

            #the question
            new = input("Il faut vous connecter : \n  1 - Inscription,\n "\
                " 2 - Connexion,\n  3 - Quitter.\n ->")

            #condition
            if new in ("1", ""):
                page("D'AUTHENTIFICATION", "inscription")

                user = self._registration(user)
                #to manage the exit option and remain user.connected False
                if user.connected == "Exit":
                    user.connected = False
                    break

            elif new == "2":
                os.system("cls")
                page("D'AUTHENTIFICATION", "connexion")
                user = self._connection(user)
                if user.connected == "Exit":
                    user.connected = False
                    break

            elif new == "3":
                break

            else:
                negatif_feed_back("Il faut donner comme réponse oui ou non !")

        return user

    def history(self, user):
        """ Permits to display the previous search.name connected to a given pseudo """

        os.system("cls")
        page("D'HISTORIQUE DE RECHERCHE")
        print("Voici les précédentes recherches que vous avez effectuées : \n")

        try:
            sql = "SELECT DATE_FORMAT(Search.day_date, '%c-%b-%y %H:%i') AS date,"\
            "prod.category, prod.name as product, Search.criterion, sub.name as substitute "\
            "FROM Search INNER JOIN Product AS prod ON Search.product_id = prod.id "\
            "INNER JOIN Product AS sub ON Search.substitute_id = sub.id "\
            "WHERE Search.user_id = {} ORDER BY 'date' DESC;".format(user.id)

            self.my_cursor.execute(sql)
            resultat = self.my_cursor.fetchall()
            if resultat == []:
                return "Aucun résultat trouvé dans votre historique de recherche."
            chain = "- "*35
            chain += "\n"
            chain += "  Date | Categorie | Produit | Critère | Substitut\n"
            for i in resultat:
                chain += " {} | {} | {} | {} | {} ".format(i[0], i[1], i[2], i[3], i[4])
                chain += "\n"
                chain += "* "*35
                chain += "\n"

            return chain
        except Exception as error:
            raise error
