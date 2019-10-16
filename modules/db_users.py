""" This script contains the database object and all methodes it needs"""

import os
import time
import mysql.connector
import modules.database as db
import modules.interactions as interactions



def negatif_feed_back(msg):
    """ display a negative feed_back message and let 1sec to read it """
    print("\n", msg, "\n")
    time.sleep(1)

def page(title, *supp):
    os.system("cls")
    print("\n", "-"*30, " PAGE {} ".format(title), "-"*30, "\n")
    if supp:
        print("- - - - {} - - - -".format(supp))
class DbUser(db.Database):
    """class that manage the _connection to the database and the fonction related to db"""

    COLUMNS = 'name, labels, additives, packagings,nutrition_grade, nova_group, traces, manufacturing_places_tags,\
    minerals_tags, palm_oil, composition, link, quantity, brands, nutriments'


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

        while True:

            #no need to use the try expression
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
                else:
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
            sql = """SELECT DATE_FORMAT(Search.day_date, '%c-%b-%y %H:%i'),
                            Product.category,
                            Product.name,
                            Search.criterion,
                            (SELECT Product.name FROM Product WHERE id = Search.substitute_id) FROM Search
            INNER JOIN Product ON Search.product_id = Product.id
            WHERE Search.user_id = '{}' ORDER BY 'date' DESC;""".format(user.id)

            self.my_cursor.execute(sql)
            resultat = self.my_cursor.fetchall()
            if resultat == [] :
                return "Aucun résultat trouvé dans votre historique de recherche."
            chain = "- "*35
            chain += "\n"
            chain += "  Date | Categorie | Produit | Critère | Substitut\n"
            for i in resultat:
                chain +=  " {} | {} | {} | {} | {} ".format(i[0], i[1], i[2], i[3], i[4])
                chain += "\n"
                chain += "* "*35
                chain += "\n"

            return chain
        except Exception as error:
            raise error

    def get_more_info(self, user):
        """User chooses a prod or a sub and give 1 word (or more), functions makes a search"""
        os.system("cls")
        print("\n", "-"*20, " PAGE D'AFFICHAGE DE LA FICHE D'UN SUBSTITUT ", "-"*20, "\n")
        while True:
            given_word = input("\nDonnez moi un élément pour la recherche :\n ->")

            sql = 'SELECT Substitute.name, Substitute.category, '\
            'GROUP_CONCAT(Label.name),GROUP_CONCAT(Brand.name),Substitute.link FROM Substitute '\
            'INNER JOIN Search ON Search.substitute_id = Substitute.id '\
            'INNER JOIN Label ON Label.substitute_id = Substitute.id '\
            'INNER JOIN Brand ON Brand.substitute_id = Substitute.id '\
            'WHERE Search.user_id = {} AND Substitute.name LIKE "%{}%";'.format(user.id, given_word)

            try: #necessary because resultat[0] can raise an error
                resultat = self.my_cursor.execute(sql)
                resultat = self.my_cursor.fetchall()
                tup = resultat[0]
                sheet = sub.Substitute(tup[0], tup[1], tup[2], tup[3], tup[4])
                input("{} \nTouche 'entrer' pour continuer".format(sheet))
                return True

            except:
                while True:
                    action = input("\n---------- Erreur ----------\nLa recherche n'a rien donné."\
                        " Vous devriez vérifier revenir au menu pour vérifier votre "\
                        "historique de recherche.\n"\
                        "Que voulez-vous faire ?\n"\
                        "  1 - Donner un autre mot,\n"\
                        "  2 - Revenir au ménu principal. \n")
                    if action == "1":
                        break
                    elif action == "2":
                        return True
                    else:
                        print("Je n'ai pas compris ! ")
