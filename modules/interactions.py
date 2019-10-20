""" Creates the Interactions class """
import os
import time

class Interactions():
    """ This class shows informations to user and asks questions """

    TUP_CATEGORY = ("Jus de fruits", "Céréales", "Confiture", "Barre chocolatee",\
    "Lait", "Chips", "Bretzels", "Yaourts", "Poissons", "Gâteaux", \
    "Pains de mie", "Charcuterie", "Pizzas", "Tartes salées", "Spaghetti", "Riz",\
    "Glaces", "Chocolat noir", "Soupes", "Compotes")

    TUP_PRECISION = ("Produit sans Huile de Palme", "Produit venant de France", "Produit Bio")

    def negatif_feed_back(self, msg):
        """ displays a negatif feed back then 1 sec break """
        print("\n", msg, "\n")
        time.sleep(1)

    def display_title(self, msg):
        """ displays a title a the top of the page """
        os.system("cls")
        print("\n", "-"*30, " PAGE DE RECHERCHE ", "-"*30)
        print(".... {} \n".format(msg))

    def input_cat_prod(self, wanted, my_list):
        """ Lets the user choose a cat """
        print("Ecrivez un nombre pour choisir votre {} :".format(wanted))
        count = 1

        for i in my_list:
            print("\t{} -> {}".format(count, i))
            count += 1
        print("** ** "*9)
        print("     ----- 21 : Revenir au menu principal -----")
        print("** ** "*9)
        ind = input(">")

        return ind

    def display_choice_cat(self, my_user):
        """ permits user to make a choice among 20 categories"""
        answer = None
        while answer == None:
        #loop in order to repeat the input question until an acceptable answer
            self.display_title("Choisir une catégorie")
            if not my_user.connected:
                print("/!\ ATTENTION : vous n'êtes pas connecté, aucune sauvegarde "\
                        "de recherche n'aura lieue !\n")
            ind = self.input_cat_prod("catégorie", self.TUP_CATEGORY) #input for cat
            answer = self._check_answer(ind, self.TUP_CATEGORY,\
                "Un nombre entre 1 et 21 est attendu ! ")
        return answer

    def _check_answer(self, ind, my_list, error_msg):
        """ For each input check the answer"""
        try:

            if ind == "21":
                print("Retour au menu principal ! ")
                time.sleep(1)
                return 'menu'
            elif int(ind) < 21:
                return my_list[int(ind)-1]
            else:
                self.negatif_feed_back(error_msg)
                return None
        except Exception:
            self.negatif_feed_back(error_msg)
            return None

    def conclusion_choice(self, cat, prod):
        """ Displays the choice done"""

        print("\n\n\n")
        print("* * "*20)
        print("\nVous avez choisi : {} > {}\n".format(cat, prod))
        print("* * "*20)
        print("\n\n\n")

    def _display_prod_info(self, info_products):
        """ Creates a tab to display infos about product """

        self.display_title("Afficher le produit")
        chain = ""
        for key in info_products:
            chain += "------"*15
            chain += "\n{} : {}\n".format(key, info_products[key])
        chain += "------"*15
        return chain

    def get_precision(self):
        """ return a more precise choice concerning the responsible sub"""
        tupp = self.TUP_PRECISION #for place
        while True:
            precision = input("J'ai besoin d'affiner votre recherche, je vous propose 3 \
                nouveaux critères:\n1/ {},\n2/ {},\n3/ {},\n4/ Revenir au menu principal.\n>".\
                format(tupp[0], tupp[1], tupp[2]))
            if precision in ["1", "2", "3", "4"]:
                return precision
            else:
                self.negatif_feed_back("La réponse attendue doit être 1, 2, 3 ou 4 !")

    def after_search(self, number):
        """ Ask the user wether he wants to make another search"""

        loop = True
        if number == "2":
            while loop:
                answer = input("Que voulez-vous faire ?"\
                "\n1/ Faire une autre recherche,\n2/ Terminer\n>")
                if answer in ["1", "2"]:
                    return answer
                self.negatif_feed_back("Réponse attendue 1 ou 2 ! ")
        elif number == "3":
            while loop:
                answer = input("Que voulez-vous faire ?"\
                "\n1/ Afficher plus d'informations,\n2/ Faire une autre recherche,\n3/ Terminer\n>")
                if answer in ["1", "2", "3"]:
                    return answer
                self.negatif_feed_back("Réponse attendue 1, 2 ou 3 ! ")


